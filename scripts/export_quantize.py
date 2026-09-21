#!/usr/bin/env python
"""Export the fine-tuned model to static-shape ONNX and quantize it for the Snapdragon NPU.

    python scripts/export_quantize.py --model-dir models/review_transformer

Produces in --model-dir:
    model.fp32.onnx   float baseline (also runs on the NPU in FP16 via the QNN EP)
    model.qdq.onnx    QDQ-quantized model (weights 8-bit, activations 8- or 16-bit)

Notes
-----
* Shapes are fixed at [1, max_len]; the HTP backend prefers static shapes.
* Transformers often lose accuracy with 8-bit activations. Default here is 16-bit
  activations (W8A16). Always compare F1 with benchmarks/run_benchmark.py --data.
* Quantization helpers live in onnxruntime.quantization.execution_providers.qnn; their
  signatures can change between onnxruntime releases, so pin the version that works.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pandas as pd
import torch
from onnxruntime.quantization import CalibrationDataReader, QuantType, quantize
from onnxruntime.quantization.execution_providers.qnn import (
    get_qnn_qdq_config, qnn_preprocess_model)
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class _LogitsOnly(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        return self.model(input_ids=input_ids, attention_mask=attention_mask).logits


class _Calib(CalibrationDataReader):
    def __init__(self, tok, texts, max_len):
        enc = tok(list(texts), truncation=True, padding="max_length",
                  max_length=max_len, return_tensors="np")
        self._items = [
            {"input_ids": enc["input_ids"][i:i + 1].astype(np.int64),
             "attention_mask": enc["attention_mask"][i:i + 1].astype(np.int64)}
            for i in range(len(texts))
        ]
        self._it = iter(self._items)

    def get_next(self):
        return next(self._it, None)

    def rewind(self):
        self._it = iter(self._items)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--calib", default=None, help="CSV with a 'text' column (default: <model-dir>/calib.csv)")
    ap.add_argument("--calib-n", type=int, default=128)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--act-bits", type=int, choices=(8, 16), default=16)
    args = ap.parse_args()

    out = Path(args.model_dir)
    tok = AutoTokenizer.from_pretrained(out)
    try:
        model = AutoModelForSequenceClassification.from_pretrained(out, attn_implementation="eager")
    except (TypeError, ValueError):
        model = AutoModelForSequenceClassification.from_pretrained(out)
    wrapper = _LogitsOnly(model.eval()).eval()

    sample = tok("This product changed my life, five stars!!!", truncation=True,
                 padding="max_length", max_length=args.max_len, return_tensors="pt")
    ids, mask = sample["input_ids"].long(), sample["attention_mask"].long()

    # 1) Export FP32, static shapes -------------------------------------------------
    fp32 = out / "model.fp32.onnx"
    export_kw = dict(input_names=["input_ids", "attention_mask"], output_names=["logits"],
                     opset_version=17)
    with torch.no_grad():
        try:
            torch.onnx.export(wrapper, (ids, mask), str(fp32), dynamo=False, **export_kw)
        except TypeError:  # older torch without the dynamo kwarg
            torch.onnx.export(wrapper, (ids, mask), str(fp32), **export_kw)
        ref = wrapper(ids, mask).numpy()

    got = ort.InferenceSession(str(fp32), providers=["CPUExecutionProvider"]).run(
        None, {"input_ids": ids.numpy(), "attention_mask": mask.numpy()})[0]
    diff = float(np.abs(ref - got).max())
    print(f"FP32 ONNX vs torch max |diff| = {diff:.2e}")
    if diff > 1e-3:
        raise SystemExit("ONNX export does not match the torch model; aborting.")

    # 2) Quantize for QNN -----------------------------------------------------------
    calib_csv = Path(args.calib) if args.calib else out / "calib.csv"
    texts = pd.read_csv(calib_csv)["text"].dropna().astype(str).tolist()[: args.calib_n]
    reader = _Calib(tok, texts, args.max_len)

    pre = out / "model.fp32.pre.onnx"
    modified = qnn_preprocess_model(str(fp32), str(pre))
    src = pre if modified else fp32

    act = QuantType.QUInt16 if args.act_bits == 16 else QuantType.QUInt8
    cfg = get_qnn_qdq_config(str(src), reader, activation_type=act, weight_type=QuantType.QUInt8)
    qdq = out / "model.qdq.onnx"
    quantize(str(src), str(qdq), cfg)
    if pre.exists():
        pre.unlink()

    print(f"wrote {fp32.name} ({fp32.stat().st_size / 1e6:.1f} MB) and "
          f"{qdq.name} ({qdq.stat().st_size / 1e6:.1f} MB), W8A{args.act_bits}")
    print("Next: python benchmarks/run_benchmark.py --model-dir", out, "--data", out / "val.csv")


if __name__ == "__main__":
    main()
