"""
Builds test_samples/from_acord/Business_and_Commercial_Contracts/*.pdf from
real clauses in your project's own ACORD dataset (data/acord/), instead of
synthetic text.

IMPORTANT SCOPE NOTE: ACORD (Atticus Clause Retrieval Dataset) is a clause-
level benchmark built entirely from real commercial contracts filed with the
US SEC (EDGAR). Its 9 clause categories (Limitation of Liability,
Indemnification, Governing Law, Term, IP ownership/licence, etc.) are all
"Business and Commercial Contracts" material — it contains no real estate,
estate planning, or litigation documents at all. So this script only
produces real-world test PDFs for ONE of the app's four categories. You
still need to source your own real PDFs for Real Estate, Estate Planning,
and Litigation (see tests/README.md) — ACORD simply has no equivalent data
for those.

To keep this a genuine held-out test (not testing against data the
retrieval model may have been tuned on), only clauses referenced by
qrels/test.tsv — ACORD's own test split — are used, never train/valid.

Usage:
    pip install reportlab
    python tests/build_acord_samples.py
    python tests/evaluate_categories.py
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

ACORD_DIR = (
    Path(__file__).resolve().parent.parent
    / "data" / "acord" / "extracted" / "ACORD Dataset & ReadMe (external)"
)
CORPUS_PATH = ACORD_DIR / "corpus.jsonl"
TEST_QRELS_PATH = ACORD_DIR / "qrels" / "test.tsv"
OUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "test_samples" / "from_acord" / "Business_and_Commercial_Contracts"
)

import os

NUM_DOCS = 15          # how many pseudo-documents (PDFs) to build
CLAUSES_PER_DOC = 7    # real clauses stitched together per pseudo-document
# Seed is overridable via env var so a *different*, previously-unseen batch
# can be pulled to sanity-check the classifier after any tuning — tuning
# against one fixed sample and re-testing on the same sample is optimistic.
SEED = int(os.environ.get("ACORD_SAMPLE_SEED", "42"))


def _load_test_split_corpus_ids() -> set[str]:
    ids = set()
    with open(TEST_QRELS_PATH, encoding="utf-8") as f:
        next(f)  # header row
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 3:
                ids.add(parts[1])
    return ids


def _load_corpus() -> dict[str, str]:
    corpus = {}
    with open(CORPUS_PATH, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            corpus[d["_id"]] = d["text"]
    return corpus


def _write_pdf(text: str, out_path: Path) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    story = []
    for para in re.split(r"\n\s*\n", text.strip()):
        clean = para.strip().replace("\n", "<br/>")
        if not clean:
            continue
        story.append(Paragraph(clean, styles["Normal"]))
        story.append(Spacer(1, 10))
    doc.build(story)


def main() -> None:
    if not CORPUS_PATH.exists() or not TEST_QRELS_PATH.exists():
        raise SystemExit(
            f"ACORD dataset not found under {ACORD_DIR}. "
            "Make sure data/acord/extracted/... is present (it ships with the repo)."
        )

    test_ids = _load_test_split_corpus_ids()
    corpus = _load_corpus()
    # Sort ids first: Python's set iteration order is randomised per-process
    # (hash randomisation), so iterating the set directly would silently
    # give a *different* base ordering on every run even with the same
    # SEED below — making the "reproducible" sample not actually
    # reproducible across process restarts. Sorting first fixes the base
    # order deterministically; the seeded shuffle then reorders it the
    # same way every time.
    test_clauses = [corpus[cid] for cid in sorted(test_ids) if cid in corpus]

    print(f"Loaded {len(test_clauses)} real clauses from ACORD's held-out test split "
          f"(out of {len(corpus)} total corpus entries).")

    random.Random(SEED).shuffle(test_clauses)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    needed = NUM_DOCS * CLAUSES_PER_DOC
    if len(test_clauses) < needed:
        raise SystemExit(f"Not enough test-split clauses ({len(test_clauses)}) for "
                          f"{NUM_DOCS} docs x {CLAUSES_PER_DOC} clauses each.")

    for doc_idx in range(NUM_DOCS):
        chunk = test_clauses[doc_idx * CLAUSES_PER_DOC:(doc_idx + 1) * CLAUSES_PER_DOC]
        # Real clause text, verbatim from ACORD/SEC filings, stitched into one
        # pseudo-document with a generic heading — no synthetic wording added.
        body = "COMMERCIAL AGREEMENT (Excerpted Clauses)\n\n" + "\n\n".join(
            f"{i+1}. {clause}" for i, clause in enumerate(chunk)
        )
        out_path = OUT_DIR / f"acord_test_{doc_idx+1:02d}.pdf"
        _write_pdf(body, out_path)

    print(f"Wrote {NUM_DOCS} PDFs (real ACORD test-split clauses) -> {OUT_DIR}")


if __name__ == "__main__":
    main()
