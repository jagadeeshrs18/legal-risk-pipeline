# Explainable legal-contract risk pipeline

Research prototype implementing:

1. ACORD dense vector retrieval;
2. comparison of three embedding models;
3. Recall@5, Recall@10, MRR@10 and nDCG@10;
4. CUAD clause-type extraction;
5. ContractNLI entailment/contradiction/not-mentioned detection;
6. gated, explainable risk scoring.

This is a research aid, not legal advice. Public datasets are predominantly US commercial contracts. Have qualified Indian legal experts validate labels, rules and outputs before Indian deployment.

## Setup

Use Python 3.10 or 3.11.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Download official datasets:

```bash
git clone https://github.com/TheAtticusProject/acord.git data/acord
git clone https://github.com/TheAtticusProject/cuad.git data/cuad_repo
git clone https://github.com/stanfordnlp/contract-nli.git data/contract_nli_repo
unzip data/cuad_repo/data.zip -d data/cuad
```

## 1–3: compare embeddings on ACORD

Locate the directory containing `corpus.jsonl`, `queries.jsonl` and `qrels/`.

```bash
python -m legalrisk.evaluate_acord \
  --data-dir data/acord \
  --output results/acord_metrics.csv
```

The loader searches subdirectories automatically. A qrel rating `>= 2` is considered relevant by default; change it using `--min-relevance`.

## 4: train/evaluate CUAD clause extraction

```bash
python -m legalrisk.cuad \
  --train data/cuad/CUAD_v1.json \
  --output models/cuad
```

The command fine-tunes an extractive QA model. Each CUAD question/category becomes the clause type. For a quick CPU smoke test add `--max-train 100 --epochs 1`.

## 5: train/evaluate ContractNLI

Find `train.json`, `dev.json` and `test.json` in the cloned repository, then:

```bash
python -m legalrisk.contract_nli \
  --data-dir data/contract_nli_repo \
  --output models/contract_nli
```

The script converts each hypothesis/document pair into a three-way sequence-classification example and reports macro-F1. Long contracts are truncated in this baseline; a production study should use evidence-span retrieval before NLI.

## 6: risk scoring and API

Edit `risk_policy.json` to reflect the contract type, party perspective and jurisdiction. Start the API:

```bash
uvicorn legalrisk.api:app --reload
```

Then POST JSON to `/score`:

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

Risk scoring is refused unless `results/quality_gates.json` exists and all gates pass. Create it after evaluation:

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

