from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
from datasets import Dataset, DatasetDict
from sklearn.metrics import classification_report
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer

LABELS = {"entailment": 0, "contradiction": 1, "notmentioned": 2,
          "not_mentioned": 2, "neutral": 2}


def locate(root: Path, split: str):
    found = list(root.rglob(f"{split}.json"))
    if not found: raise FileNotFoundError(f"No {split}.json below {root}")
    return found[0]


def load_split(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    docs = raw.get("documents", raw if isinstance(raw, list) else [])
    rows = []
    for doc in docs:
        text = doc.get("text") or "\n".join(
            s if isinstance(s, str) else s.get("text", "") for s in doc.get("spans", [])
        )
        hypotheses = raw.get("labels", raw.get("hypotheses", {})) if isinstance(raw, dict) else {}
        sets = doc.get("annotation_sets", doc.get("annotations", []))
        if isinstance(sets, dict): sets = sets.values()
        for item in sets:
            annotations = item.get("annotations", item) if isinstance(item, dict) else item
            if isinstance(annotations, dict):
                annotations = [{"hypothesis_id": key, **(value if isinstance(value, dict) else {"label": value})}
                               for key, value in annotations.items()]
            for ann in annotations:
                hid = str(ann.get("hypothesis_id", ann.get("label_id", "")))
                definition = hypotheses.get(hid, {}) if isinstance(hypotheses, dict) else {}
                if isinstance(definition, str): definition = {"hypothesis": definition}
                hypothesis = ann.get("hypothesis", ann.get("statement", definition.get("hypothesis", definition.get("text", ""))))
                label = str(ann.get("label", ann.get("choice", ""))).lower().replace(" ", "").replace("-", "_")
                if hypothesis and label in LABELS:
                    rows.append({"hypothesis": hypothesis, "contract": text, "label": LABELS[label]})
    if not rows:
        raise ValueError("ContractNLI schema was not recognized; inspect the official JSON and adapt load_split")
    return Dataset.from_list(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("models/contract_nli"))
    p.add_argument("--model", default="microsoft/deberta-v3-base")
    p.add_argument("--epochs", type=float, default=2)
    args = p.parse_args()
    data = DatasetDict({s: load_split(locate(args.data_dir, s)) for s in ("train", "dev", "test")})
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    encoded = data.map(lambda b: tokenizer(b["hypothesis"], b["contract"], truncation=True,
                                           max_length=512, padding="max_length"),
                       batched=True, remove_columns=["hypothesis", "contract"])
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=3)
    def metrics(pred):
        y = pred.label_ids; yh = np.argmax(pred.predictions, axis=-1)
        report = classification_report(y, yh, output_dict=True, zero_division=0)
        return {"macro_f1": report["macro avg"]["f1-score"], "accuracy": report["accuracy"]}
    training = TrainingArguments(output_dir=str(args.output), num_train_epochs=args.epochs,
                                 per_device_train_batch_size=4, per_device_eval_batch_size=8,
                                 learning_rate=2e-5, eval_strategy="epoch", save_strategy="epoch",
                                 load_best_model_at_end=True, metric_for_best_model="macro_f1", report_to=[])
    trainer = Trainer(model=model, args=training, train_dataset=encoded["train"],
                      eval_dataset=encoded["dev"], compute_metrics=metrics, tokenizer=tokenizer)
    trainer.train(); print(trainer.evaluate(encoded["test"])); trainer.save_model(str(args.output))


if __name__ == "__main__":
    main()
