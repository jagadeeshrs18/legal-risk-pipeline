from __future__ import annotations

import csv
import json
from pathlib import Path


def find_beir_root(root: Path) -> Path:
    for corpus in root.rglob("corpus.jsonl"):
        parent = corpus.parent
        if (parent / "queries.jsonl").exists() and (parent / "qrels").exists():
            return parent
    raise FileNotFoundError("Could not find corpus.jsonl, queries.jsonl and qrels/ below " + str(root))


def _jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def load_beir(root: Path, split: str = "test"):
    root = find_beir_root(root)
    corpus = {}
    for row in _jsonl(root / "corpus.jsonl"):
        did = str(row.get("_id", row.get("id")))
        corpus[did] = (str(row.get("title", "")) + "\n" + str(row.get("text", ""))).strip()
    queries = {}
    for row in _jsonl(root / "queries.jsonl"):
        qid = str(row.get("_id", row.get("id")))
        queries[qid] = str(row.get("text", row.get("query", "")))
    candidates = [root / "qrels" / f"{split}.tsv", root / "qrels" / f"{split}.txt"]
    qrel_path = next((p for p in candidates if p.exists()), None)
    if qrel_path is None:
        files = list((root / "qrels").glob("*"))
        if not files:
            raise FileNotFoundError("No qrels file found")
        qrel_path = files[0]
    qrels = {}
    with qrel_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            qid = str(row.get("query-id", row.get("query_id", row.get("qid"))))
            did = str(row.get("corpus-id", row.get("doc_id", row.get("docid"))))
            score = int(float(row.get("score", row.get("relevance", 0))))
            qrels.setdefault(qid, {})[did] = score
    active = sorted(set(queries) & set(qrels))
    return corpus, {q: queries[q] for q in active}, {q: qrels[q] for q in active}

