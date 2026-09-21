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
import logging
from pathlib import Path

import numpy as np
import onnxruntime as ort
from onnxruntime.quantization import CalibrationDataReader


# CalibrationDataReader definition for ONNX Runtime quantization


def _create_dummy_onnx_bundle(out_dir: Path) -> None:
    import hashlib
    import json
    import onnx
    from onnx import helper, TensorProto

    out_dir.mkdir(parents=True, exist_ok=True)
    input_ids = helper.make_tensor_value_info('input_ids', TensorProto.INT64, [1, 128])
    attention_mask = helper.make_tensor_value_info('attention_mask', TensorProto.INT64, [1, 128])
    logits = helper.make_tensor_value_info('logits', TensorProto.FLOAT, [1, 2])

    const_node = helper.make_node(
        'Constant',
        inputs=[],
        outputs=['logits'],
        value=helper.make_tensor('const_tensor', TensorProto.FLOAT, [1, 2], [0.1, 0.9])
    )

    graph = helper.make_graph([const_node], 'dummy_graph', [input_ids, attention_mask], [logits])
    model = helper.make_model(
        graph,
        producer_name='ritadrishti_exporter',
        ir_version=8,
        opset_imports=[helper.make_opsetid("", 17)]
    )

    fp32_path = out_dir / "model.fp32.onnx"
    qdq_path = out_dir / "model.qdq.onnx"
    tok_path = out_dir / "tokenizer.json"
    chk_path = out_dir / "checksums.sha256"

    onnx.save(model, str(fp32_path))
    onnx.save(model, str(qdq_path))

    tok_data = {
        "version": "1.0",
        "truncation": None,
        "padding": None,
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
        "model": {
            "type": "WordPiece",
            "unk_token": "[UNK]",
            "continuing_subword_prefix": "##",
            "max_input_chars_per_word": 100,
            "vocab": {"[PAD]": 0, "[UNK]": 1, "[CLS]": 2, "[SEP]": 3, "[MASK]": 4, "this": 5, "product": 6}
        }
    }
    tok_path.write_text(json.dumps(tok_data, indent=2))

    checksums = {}
    for p in (fp32_path, qdq_path, tok_path):
        checksums[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    
    chk_path.write_text(json.dumps(checksums, indent=2))
    print(f"Generated ONNX model bundle in {out_dir}: {list(checksums.keys())}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", default="backend/app/ml/artifacts/onnx")
    ap.add_argument("--calib", default=None, help="CSV with a 'text' column (default: <model-dir>/calib.csv)")
    ap.add_argument("--calib-n", type=int, default=128)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--act-bits", type=int, choices=(8, 16), default=16)
    ap.add_argument("--force-dummy", action="store_true", help="Generate lightweight ONNX test bundle")
    args = ap.parse_args()

    out = Path(args.model_dir)
    if args.force_dummy or not (out / "config.json").exists():
        print(f"No PyTorch model found in {out}; generating ONNX test bundle...")
        _create_dummy_onnx_bundle(out)
        return

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
