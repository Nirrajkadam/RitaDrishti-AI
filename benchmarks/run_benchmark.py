#!/usr/bin/env python
"""Benchmark FP32 vs quantized model on CPU and (when available) the Snapdragon NPU.

    python benchmarks/run_benchmark.py --model-dir models/review_transformer \
        --data models/review_transformer/val.csv

Every row is labelled with the providers ONNX Runtime *actually* activated. NPU rows are
only produced when the QNN execution provider exists on this machine, so numbers from a
non-Snapdragon machine are never presented as NPU numbers.

Timing covers model inference only (tokenization is done beforehand). Latency is per
review at batch size 1.
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "app" / "ml"))
from accelerator import create_session, qnn_available  # noqa: E402
from onnx_engine import load_encoder  # noqa: E402


def load_csv(path: Path, limit: int):
    import csv

    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))[:limit]
    return [r["text"] for r in rows], [int(r["label"]) for r in rows]


def run(session, ids, mask):
    return session.run(None, {"input_ids": ids, "attention_mask": mask})[0]


def measure(session, feeds, warmup: int, iters: int) -> dict:
    for i in range(warmup):
        run(session, *feeds[i % len(feeds)])
    times = []
    for i in range(iters):
        ids, mask = feeds[i % len(feeds)]
        t0 = time.perf_counter_ns()
        run(session, ids, mask)
        times.append((time.perf_counter_ns() - t0) / 1e6)
    times.sort()
    return {
        "p50_ms": statistics.median(times),
        "p95_ms": times[min(len(times) - 1, int(0.95 * len(times)))],
        "mean_ms": statistics.fmean(times),
        "reviews_per_s": 1000.0 / statistics.fmean(times),
    }


def quality(session, feeds, labels) -> dict:
    from sklearn.metrics import accuracy_score, f1_score

    preds = [int(np.argmax(run(session, ids, mask), axis=-1)[0]) for ids, mask in feeds]
    return {"accuracy": float(accuracy_score(labels, preds)),
            "f1": float(f1_score(labels, preds, zero_division=0))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--data", default=None, help="CSV with text,label for accuracy/F1")
    ap.add_argument("--eval-n", type=int, default=500)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--out", default=str(ROOT / "benchmarks" / "results.json"))
    args = ap.parse_args()

    mdir = Path(args.model_dir)
    encode = load_encoder(mdir, args.max_len)
    texts, labels = (load_csv(Path(args.data), args.eval_n) if args.data
                     else (["Great product, works as described.", "BEST EVER!!! buy now!!!"] * 8, None))
    feeds = [encode(t) for t in texts]

    models = {"FP32": mdir / "model.fp32.onnx", "QDQ": mdir / "model.qdq.onnx"}
    plan = [(p, m, "cpu") for p, m in models.items()]
    if qnn_available():
        plan += [(p, m, "npu") for p, m in models.items()]
    else:
        print("QNN execution provider not available here: NPU rows omitted.")

    results = []
    for prec, path, mode in plan:
        if not path.exists():
            print(f"skip {prec}/{mode}: {path.name} missing")
            continue
        try:
            session, info = create_session(path, mode)
        except Exception as exc:
            print(f"skip {prec}/{mode}: {str(exc)[:120]}")
            continue
        row = {"precision": prec, "requested": mode, "backend": info.label,
               "providers": list(info.active_providers), "size_mb": path.stat().st_size / 1e6,
               **measure(session, feeds, args.warmup, args.iters)}
        if labels is not None:
            row.update(quality(session, feeds, labels))
        results.append(row)
        print(f"done {prec}/{info.label}: p50={row['p50_ms']:.2f} ms")

    print("\n| Model | Backend | p50 ms | p95 ms | Reviews/s | Size MB | Acc | F1 |")
    print("|---|---|---|---|---|---|---|---|")
    for r in results:
        acc = f"{r['accuracy']:.3f}" if "accuracy" in r else "-"
        f1 = f"{r['f1']:.3f}" if "f1" in r else "-"
        print(f"| {r['precision']} | {r['backend']} | {r['p50_ms']:.2f} | {r['p95_ms']:.2f} | "
              f"{r['reviews_per_s']:.1f} | {r['size_mb']:.1f} | {acc} | {f1} |")

    Path(args.out).write_text(json.dumps({
        "machine": {"platform": platform.platform(), "machine": platform.machine(),
                    "processor": platform.processor(), "onnxruntime": ort.__version__},
        "settings": {"max_len": args.max_len, "warmup": args.warmup, "iters": args.iters,
                     "eval_samples": len(labels) if labels else 0},
        "results": results}, indent=2))
    print(f"\nsaved {args.out}")


if __name__ == "__main__":
    main()
