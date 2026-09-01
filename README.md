# Explainable legal-document risk analyzer

A research prototype that reads an uploaded legal document (PDF), classifies
which of four broad categories it belongs to, flags risky or missing
clauses with an explainable, rule-based score, and suggests concrete
rewording to reduce that risk — surfaced through a small Flask web app, with
an underlying ACORD-based dense-retrieval/evaluation pipeline available for
research use via the CLI.

**This is a research aid, not legal advice.** The clause-risk rules and
document-category signals were authored by hand and validated against a mix
of synthetic and real (US, SEC-filed) commercial-contract text; they have
not been reviewed by a qualified lawyer in any jurisdiction. Have a
qualified legal professional validate labels, rules, and outputs before any
real-world use, especially outside the jurisdictions the rules were written
with in mind (India / US).

## What it does

1. **Classifies the document into one of four categories** before analysing
   it, and refuses to run the (expensive) analysis if the uploaded PDF
   doesn't confidently match the category section it was dropped into —
   telling the user which category it actually looks like instead:
   - **Business and Commercial Contracts** — Employment Agreement, NDA,
     Service Agreement, Vendor Agreement (chosen via a sub-type dropdown)
   - **Real Estate and Property Documents** — lease/rental agreements
   - **Estate Planning Documents** — wills, powers of attorney
   - **Court and Litigation Pleadings** — complaints, legal notices
2. **Segments the document into clauses** and classifies each clause's type
   using a heading-alias + keyword-scoring engine, with a separate,
   hand-written rule set per category (`legalrisk/flask_analyzer.py` for
   commercial contracts, `legalrisk/domain_rules.py` for the other three).
3. **Scores risk per clause** against regex-based risky/protective patterns,
   plus a "missing required clause" penalty for clause types that should be
   present but aren't, combined into a single 0–100 score with a Low/
   Medium/High/Critical band.
4. **Scores risk from the selected perspective**, not just generically. Most
   clause-risk rules were authored to protect one side of a two-sided
   relationship (e.g. the Customer in a Service Agreement, the Tenant in a
   lease, the Employee in an employment contract, the Plaintiff in a
   pleading). Selecting the *other* side (Vendor, Landlord, Employer,
   Defendant) excludes that clause from the score and instead labels it
   "favours you" — the same clause, correctly reframed depending on who's
   asking. NDA and Estate Planning documents don't have a clean two-sided
   adversarial split, so they stay neutral regardless of perspective.
5. **Suggests a safer redraft for every risk finding** — both clauses
   flagged as risky *and* required clauses found to be missing entirely —
   pulled from a hand-curated dataset (`data/clause_suggestions.json`,
   150+ entries across all four categories) keyed by clause type and the
   specific issue detected. If a genuinely new issue is ever encountered
   that isn't in the dataset yet, a clause-type-appropriate generic
   suggestion is generated on the fly and **persisted back into the
   dataset**, so the suggestion set grows over time instead of silently
   failing to offer advice (see `legalrisk/suggestions.py`).
6. **Retrieves similar precedent clauses via dense vector search** against
   ACORD (real commercial-contract clauses from US SEC filings) using a
   sentence-embedding model + FAISS, shown alongside each finding as
   supporting evidence — similarity is retrieval evidence, not a legal-risk
   verdict on its own.

## Setup

Use Python 3.10–3.13 (tested on 3.13).

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The ACORD dataset (real commercial-contract clauses, MIT-licensed) ships
with this repo under `data/acord/` — no separate download needed for the web
app or its tests. `indexes/` contains a prebuilt FAISS index over that
corpus, also included, so the app works out of the box without re-embedding
anything.

## Running the web app (main deliverable)

```bash
python flask_app.py
```

Open `http://127.0.0.1:5000`. The homepage shows four upload sections, one
per category. Pick the one matching your document, upload a searchable
(non-scanned) PDF, choose a perspective and jurisdiction, and submit. The
report page shows the overall score, missing protections (each with a
suggested clause to add), and every clause finding (each with detected risk
indicators and a suggested safer redraft) — with a "Download Word report"
option for an offline copy.

## Testing category-classification accuracy

```bash
pip install -r tests/requirements-test.txt   # installs reportlab, only needed here
python tests/generate_sample_pdfs.py          # synthetic in-house dataset
python tests/build_acord_samples.py           # real ACORD test-split clauses
python tests/evaluate_categories.py           # prints accuracy + confusion matrix for both
```

Current results:

| Source | Strict accuracy | Gate accuracy* |
|---|---|---|
| In-house synthetic (105 docs, all 4 categories) | 100% (105/105) | 100% |
| Real ACORD test-split clauses (15 docs, Commercial only) | 93.3% (14/15) | 100% (15/15) |

*Gate accuracy = the document was never confidently misfiled into the
*wrong* category (an "Uncertain" prediction is a safe non-answer, not
counted as a rejection, so it passes the app's actual upload gate). See
`tests/README.md` for the full story — including two real bugs that were
found and fixed by testing against ACORD's real clauses instead of only the
synthetic set, and instructions for adding your own real, internet-sourced
PDFs to test Real Estate, Estate Planning, and Litigation (ACORD has no
data for those three).

## Research pipeline (CLI, optional)

The original ACORD retrieval-evaluation, CUAD clause-extraction, and
ContractNLI entailment-detection tooling this project started from is still
available for standalone research use, independent of the Flask app above.

### Compare embedding models on ACORD

```bash
python -m legalrisk.evaluate_acord \
  --data-dir data/acord \
  --output results/acord_metrics.csv
```

Reports Recall@5, Recall@10, MRR@10, and nDCG@10 across three embedding
models. The loader searches subdirectories automatically. A qrel rating
`>= 2` is considered relevant by default; change it using `--min-relevance`.

### Train/evaluate CUAD clause extraction

Requires the CUAD dataset, not bundled here:

```bash
git clone https://github.com/TheAtticusProject/cuad.git data/cuad_repo
unzip data/cuad_repo/data.zip -d data/cuad

python -m legalrisk.cuad \
  --train data/cuad/CUAD_v1.json \
  --output models/cuad
```

Fine-tunes an extractive QA model; each CUAD question/category becomes the
clause type. For a quick CPU smoke test add `--max-train 100 --epochs 1`.

### Train/evaluate ContractNLI

Requires the ContractNLI dataset, not bundled here:

```bash
git clone https://github.com/stanfordnlp/contract-nli.git data/contract_nli_repo

python -m legalrisk.contract_nli \
  --data-dir data/contract_nli_repo \
  --output models/contract_nli
```

Converts each hypothesis/document pair into a three-way sequence-
classification example and reports macro-F1. Long contracts are truncated
in this baseline; a production study should use evidence-span retrieval
before NLI.

### Standalone scoring API

```bash
uvicorn legalrisk.api:app --reload
```

POST JSON to `/score`:

```json
{
  "clause_type": "Limitation of Liability",
  "text": "The supplier shall have no liability under this agreement.",
  "nli_label": "contradiction",
  "retrieval_similarity": 0.83,
  "risky_precedent_similarity": 0.91,
  "missing": false
}
```

Scoring is refused unless `results/quality_gates.json` exists and all gates
in `config.yaml` pass. Create it after evaluation, e.g.:

```json
{
  "recall_at_10": 0.72,
  "clause_macro_f1": 0.78,
  "nli_macro_f1": 0.74
}
```

## Important evaluation controls

- Split by contract/document, never randomly by clause.
- Tune thresholds only on validation data.
- Report per-category scores and confidence intervals.
- Keep human-reviewed evidence with every risk label.
- Similarity is retrieval evidence, not a legal-risk decision.
- When testing the document-category classifier or the clause-risk rules
  against real documents, be explicit about which results came from data
  the rules were tuned against versus a genuinely held-out sample — the
  gap between the two is itself a meaningful, honest measurement (see
  `tests/README.md`).
