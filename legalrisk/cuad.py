from __future__ import annotations

import argparse
import json
from pathlib import Path
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, TrainingArguments, Trainer


def load_cuad(path: Path, limit=None):
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for document in raw["data"]:
        for paragraph in document["paragraphs"]:
            context = paragraph["context"]
            for qa in paragraph["qas"]:
                answer = qa.get("answers", [])[:1]
                if answer:
                    rows.append({"id": qa["id"], "question": qa["question"], "context": context,
                                 "answers": {"text": [answer[0]["text"]],
                                             "answer_start": [answer[0]["answer_start"]]}})
                if limit and len(rows) >= limit:
                    return Dataset.from_list(rows)
    return Dataset.from_list(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--train", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("models/cuad"))
    p.add_argument("--model", default="distilbert-base-uncased")
    p.add_argument("--epochs", type=float, default=2)
    p.add_argument("--max-train", type=int)
    args = p.parse_args()
    ds = load_cuad(args.train, args.max_train).train_test_split(test_size=0.15, seed=42)
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)

    def tokenize(batch):
        tokens = tokenizer(batch["question"], batch["context"], truncation="only_second",
                           max_length=384, stride=128, padding="max_length",
                           return_offsets_mapping=True)
        starts, ends = [], []
        for i, offsets in enumerate(tokens.pop("offset_mapping")):
            sequence = tokens.sequence_ids(i)
            ans_start = batch["answers"][i]["answer_start"][0]
            ans_end = ans_start + len(batch["answers"][i]["text"][0])
            cstart = next(j for j, x in enumerate(sequence) if x == 1)
            cend = len(sequence) - 1 - next(j for j, x in enumerate(reversed(sequence)) if x == 1)
            if offsets[cstart][0] > ans_start or offsets[cend][1] < ans_end:
                starts.append(0); ends.append(0); continue
            while cstart < len(offsets) and offsets[cstart][0] <= ans_start: cstart += 1
            while offsets[cend][1] >= ans_end: cend -= 1
            starts.append(cstart - 1); ends.append(cend + 1)
        tokens["start_positions"], tokens["end_positions"] = starts, ends
        return tokens

    encoded = ds.map(tokenize, batched=True, remove_columns=ds["train"].column_names)
    model = AutoModelForQuestionAnswering.from_pretrained(args.model)
    training = TrainingArguments(output_dir=str(args.output), num_train_epochs=args.epochs,
                                 per_device_train_batch_size=8, per_device_eval_batch_size=8,
                                 learning_rate=3e-5, eval_strategy="epoch", save_strategy="epoch",
                                 load_best_model_at_end=True, report_to=[])
    trainer = Trainer(model=model, args=training, train_dataset=encoded["train"],
                      eval_dataset=encoded["test"], tokenizer=tokenizer)
    trainer.train(); trainer.save_model(str(args.output)); tokenizer.save_pretrained(str(args.output))


if __name__ == "__main__":
    main()

