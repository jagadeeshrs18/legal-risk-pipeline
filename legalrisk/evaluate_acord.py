from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from .beir import load_beir
from .metrics import evaluate_run

DEFAULT_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "BAAI/bge-base-en-v1.5",
    "sentence-transformers/all-mpnet-base-v2",
]


def encode(model, model_name, texts, *, query=False, batch_size=32):
    if "bge" in model_name.lower():
        if query:
            texts = ["Represent this sentence for searching relevant passages: " + t for t in texts]
    return model.encode(texts, batch_size=batch_size, normalize_embeddings=True,
                        show_progress_bar=True, convert_to_numpy=True).astype("float32")


def evaluate_model(name, corpus, queries, qrels, batch_size, min_relevance):
    model = SentenceTransformer(name)
    doc_ids = list(corpus)
    matrix = encode(model, name, [corpus[x] for x in doc_ids], batch_size=batch_size)
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)
    qids = list(queries)
    qmatrix = encode(model, name, [queries[x] for x in qids], query=True, batch_size=batch_size)
    scores, positions = index.search(qmatrix, min(10, len(doc_ids)))
    run = {}
    for qid, score_row, position_row in zip(qids, scores, positions):
        run[qid] = [(doc_ids[int(pos)], float(score)) for score, pos in zip(score_row, position_row)]
    return evaluate_run(qrels, run, min_relevance)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("results/acord_metrics.csv"))
    p.add_argument("--split", default="test")
    p.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--min-relevance", type=int, default=2)
    args = p.parse_args()
    corpus, queries, qrels = load_beir(args.data_dir, args.split)
    records = []
    for name in tqdm(args.models, desc="Models"):
        records.append({"model": name, **evaluate_model(name, corpus, queries, qrels,
                                                         args.batch_size, args.min_relevance)})
    frame = pd.DataFrame(records).sort_values("nDCG@10", ascending=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
