#!/usr/bin/env python
"""Fine-tune a small transformer for fake-review detection.

Run this on a GPU machine or Colab (training on the laptop CPU is slow), then copy
the output folder to the Snapdragon PC after running export_quantize.py.

Input CSV columns: ``text``, ``label`` (1 = fake, 0 = genuine).

    python scripts/finetune_transformer.py --data data/reviews.csv --out models/review_transformer

Outputs (in --out): model + tokenizer.json, val.csv (held-out split, reused by the
benchmark), calib.csv (calibration samples for quantization), metrics.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          get_linear_schedule_with_warmup)


def evaluate(model, enc, labels, device, batch):
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, len(labels), batch):
            b = {k: v[i:i + batch].to(device) for k, v in enc.items()}
            preds.append(model(**b).logits.argmax(-1).cpu())
    y_pred = torch.cat(preds).numpy()
    y = labels.numpy()
    return {
        "accuracy": float(accuracy_score(y, y_pred)),
        "precision": float(precision_score(y, y_pred, zero_division=0)),
        "recall": float(recall_score(y, y_pred, zero_division=0)),
        "f1": float(f1_score(y, y_pred, zero_division=0)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="models/review_transformer")
    ap.add_argument("--base", default="distilbert-base-uncased")
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--val-frac", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.data).dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(int)
    # Deduplicate texts to prevent evaluation data leakage between train and validation splits
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    train_df, val_df = train_test_split(
        df, test_size=args.val_frac, stratify=df["label"], random_state=args.seed
    )
    print(f"train={len(train_df)} val={len(val_df)} fake_rate={df['label'].mean():.3f}")

    tok = AutoTokenizer.from_pretrained(args.base)
    model = AutoModelForSequenceClassification.from_pretrained(args.base, num_labels=2).to(device)

    def enc(texts):
        return tok(list(texts), truncation=True, padding="max_length",
                   max_length=args.max_len, return_tensors="pt")

    tr_enc, va_enc = enc(train_df["text"]), enc(val_df["text"])
    tr_y = torch.tensor(train_df["label"].values)
    va_y = torch.tensor(val_df["label"].values)

    counts = np.bincount(train_df["label"].values, minlength=2).astype(float)
    weights = torch.tensor(len(tr_y) / (2.0 * counts), dtype=torch.float, device=device)
    loss_fn = torch.nn.CrossEntropyLoss(weight=weights)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    steps = args.epochs * ((len(tr_y) + args.batch - 1) // args.batch)
    sched = get_linear_schedule_with_warmup(opt, int(0.06 * steps), steps)

    best_f1, best = -1.0, {}
    for epoch in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(len(tr_y))
        for i in range(0, len(perm), args.batch):
            idx = perm[i:i + args.batch]
            batch = {k: v[idx].to(device) for k, v in tr_enc.items()}
            loss = loss_fn(model(**batch).logits, tr_y[idx].to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            opt.zero_grad()
        m = evaluate(model, va_enc, va_y, device, args.batch)
        print(f"epoch {epoch}: loss={loss.item():.4f} " +
              " ".join(f"{k}={v:.4f}" for k, v in m.items()))
        if m["f1"] > best_f1:
            best_f1, best = m["f1"], m
            model.save_pretrained(out)
            tok.save_pretrained(out)

    val_df.to_csv(out / "val.csv", index=False)
    train_df.sample(min(512, len(train_df)), random_state=args.seed).to_csv(
        out / "calib.csv", index=False)
    (out / "metrics.json").write_text(json.dumps(
        {"base_model": args.base, "max_len": args.max_len, "val_metrics_fp32_torch": best},
        indent=2))
    print(f"saved best model (f1={best_f1:.4f}) to {out}")


if __name__ == "__main__":
    main()
