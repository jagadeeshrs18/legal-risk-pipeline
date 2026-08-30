from __future__ import annotations

import math
import numpy as np


def evaluate_run(qrels, run, min_relevance: int = 2):
    rows = []
    for qid, judged in qrels.items():
        relevant = {d for d, grade in judged.items() if grade >= min_relevance}
        if not relevant:
            continue
        ranking = run.get(qid, [])
        ids = [doc_id for doc_id, _ in ranking]
        r5 = len(relevant.intersection(ids[:5])) / len(relevant)
        r10 = len(relevant.intersection(ids[:10])) / len(relevant)
        rr = next((1.0 / i for i, d in enumerate(ids[:10], 1) if d in relevant), 0.0)
        dcg = sum((2 ** judged.get(d, 0) - 1) / math.log2(i + 1) for i, d in enumerate(ids[:10], 1))
        ideal = sorted(judged.values(), reverse=True)[:10]
        idcg = sum((2 ** g - 1) / math.log2(i + 1) for i, g in enumerate(ideal, 1))
        rows.append((r5, r10, rr, dcg / idcg if idcg else 0.0))
    if not rows:
        raise ValueError("No queries have relevant qrels at the selected threshold")
    values = np.asarray(rows)
    return dict(zip(["Recall@5", "Recall@10", "MRR@10", "nDCG@10"], values.mean(axis=0)))

