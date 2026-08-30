from __future__ import annotations

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Explainable Legal Risk Research API", version="0.1.0")


class RiskInput(BaseModel):
    clause_type: str
    text: str = Field(min_length=5)
    nli_label: str
    retrieval_similarity: float = Field(ge=-1, le=1)
    risky_precedent_similarity: float = Field(ge=-1, le=1)
    missing: bool = False


def gates():
    path = ROOT / "results" / "quality_gates.json"
    if not path.exists(): return False, "quality_gates.json is missing"
    values = json.loads(path.read_text())
    needed = {"recall_at_10": .60, "clause_macro_f1": .60, "nli_macro_f1": .60}
    failed = [f"{k}={values.get(k)} < {v}" for k, v in needed.items() if values.get(k, -1) < v]
    return not failed, "; ".join(failed)


@app.get("/health")
def health(): return {"status": "ok"}


@app.post("/score")
def score(item: RiskInput):
    passed, reason = gates()
    if not passed: raise HTTPException(409, "Risk scoring disabled: " + reason)
    policy = json.loads((ROOT / "risk_policy.json").read_text())
    rule = policy.get(item.clause_type, {"base": 10, "missing": 20, "contradiction": 15})
    components = {"base_clause_risk": rule["base"], "missing_protection": rule["missing"] if item.missing else 0,
                  "nli_contradiction": rule["contradiction"] if item.nli_label.lower() == "contradiction" else 0,
                  "risky_precedent": round(max(0, item.risky_precedent_similarity) * 25, 2)}
    total = min(100, round(sum(components.values()), 2))
    level = "critical" if total >= 80 else "high" if total >= 60 else "medium" if total >= 30 else "low"
    return {"risk_score": total, "risk_level": level, "components": components,
            "evidence": {"clause": item.text, "nli_label": item.nli_label,
                         "retrieval_similarity": item.retrieval_similarity},
            "warning": "Research output; requires review by a qualified legal professional."}

