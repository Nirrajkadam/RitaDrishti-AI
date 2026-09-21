"""
Unit tests for Snapdragon NPU accelerator module
"""

import pytest
import numpy as np
from backend.app.ml.snapdragon_opt import SnapdragonNPUAccelerator
from backend.app.ml.accelerator import qnn_available, AcceleratorInfo, CPU_EP


def test_snapdragon_npu_inference():
    accelerator = SnapdragonNPUAccelerator()
    dummy_ids = np.ones((1, 128), dtype=np.int64)
    res = accelerator.run_npu_inference(dummy_ids)

    assert "active_provider" in res
    assert "latency_ms" in res
    assert "npu_accelerated" in res
    assert len(res["output_shape"]) >= 1


def test_snapdragon_benchmark():
    accelerator = SnapdragonNPUAccelerator()
    bench = accelerator.benchmark_cpu_vs_npu(iterations=5)

    assert bench["iterations"] == 5
    assert "avg_latency_ms" in bench
    assert "p50_latency_ms" in bench
    assert "active_provider" in bench


def test_accelerator_info_dataclass():
    info = AcceleratorInfo(
        requested="auto",
        active_providers=(CPU_EP,),
        npu_active=False,
        label="CPU",
        note=None
    )
    d = info.as_dict()
    assert d["requested"] == "auto"
    assert d["active_providers"] == [CPU_EP]
    assert d["npu_active"] is False
    assert qnn_available() in [True, False]


def test_accelerator_create_session_modes(tmp_path):
    from backend.app.ml.accelerator import create_session, _qnn_backend, VALID_MODES

    assert "auto" in VALID_MODES
    assert isinstance(_qnn_backend(), str)

    # Invalid mode raises ValueError
    with pytest.raises(ValueError):
        create_session(tmp_path / "dummy.onnx", mode="invalid_mode")

    # mode='npu' when QNN not installed raises RuntimeError
    if not qnn_available():
        with pytest.raises(RuntimeError):
            create_session(tmp_path / "dummy.onnx", mode="npu")


def test_onnx_engine_helpers(tmp_path):
    from backend.app.ml.onnx_engine import _softmax, OnnxReviewEngine

    logits = np.array([[1.0, 2.0]], dtype=np.float32)
    probs = _softmax(logits)
    assert probs.shape == (1, 2)
    assert abs(float(probs.sum()) - 1.0) < 1e-5

    # OnnxReviewEngine missing model file raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        OnnxReviewEngine(tmp_path)


def test_onnx_engine_full_flow(tmp_path):
    import onnx
    from onnx import helper, TensorProto

    # Construct minimal ONNX model returning constant logits [[0.2, 0.8]]
    input_ids = helper.make_tensor_value_info('input_ids', TensorProto.INT64, [1, 128])
    attention_mask = helper.make_tensor_value_info('attention_mask', TensorProto.INT64, [1, 128])
    logits = helper.make_tensor_value_info('logits', TensorProto.FLOAT, [1, 2])

    const_node = helper.make_node(
        'Constant',
        inputs=[],
        outputs=['logits'],
        value=helper.make_tensor('const_tensor', TensorProto.FLOAT, [1, 2], [0.2, 0.8])
    )

    graph = helper.make_graph([const_node], 'dummy_graph', [input_ids, attention_mask], [logits])
    model = helper.make_model(
        graph,
        producer_name='ritadrishti_test',
        ir_version=8,
        opset_imports=[helper.make_opsetid("", 17)]
    )

    # Test model.fp32.onnx fallback
    fp32_path = tmp_path / "model.fp32.onnx"
    onnx.save(model, str(fp32_path))

    from backend.app.ml.onnx_engine import OnnxReviewEngine, load_encoder
    enc = load_encoder(tmp_path, max_len=128)
    i_ids, a_mask = enc("Test review text")
    assert i_ids.shape == (1, 128)
    assert a_mask.shape == (1, 128)

    # Test engine with cache_dir and predict_proba with multiple texts
    cache = tmp_path / "cache"
    engine = OnnxReviewEngine(tmp_path, mode="cpu", cache_dir=cache)
    score_res = engine.score("Great test review")
    assert "fake_probability" in score_res
    assert "label" in score_res
    assert "accelerator" in score_res
    assert isinstance(engine.info_dict, dict)
    assert score_res["label"] == "likely_fake"

    probs = engine.predict_proba(["Review 1", "Review 2"])
    assert len(probs) == 2

    # Test SnapdragonNPUAccelerator with model_path
    accelerator = SnapdragonNPUAccelerator(onnx_model_path=str(fp32_path), mode="cpu")
    run_res = accelerator.run_npu_inference(i_ids, a_mask)
    assert run_res["active_provider"] == CPU_EP
    bench_res = accelerator.benchmark_cpu_vs_npu(iterations=2)
    assert bench_res["iterations"] == 2


def test_tokenizer_json_load_encoder(tmp_path):
    # Test tokenizer.json parsing branch in load_encoder
    tok_json = tmp_path / "tokenizer.json"
    tok_json.write_text('{"version": "1.0", "truncation": null, "padding": null, "model": {"type": "WordPiece", "vocab": {"[PAD]": 0, "test": 1}}}')
    
    from backend.app.ml.onnx_engine import load_encoder
    enc = load_encoder(tmp_path, max_len=128)
    ids, mask = enc("test")
    assert ids.shape == (1, 128)


def test_accelerator_cache_dir_and_fp16(tmp_path):
    import onnx
    from onnx import helper, TensorProto
    from backend.app.ml.accelerator import create_session

    input_ids = helper.make_tensor_value_info('input_ids', TensorProto.INT64, [1, 128])
    logits = helper.make_tensor_value_info('logits', TensorProto.FLOAT, [1, 2])
    const_node = helper.make_node(
        'Constant',
        inputs=[],
        outputs=['logits'],
        value=helper.make_tensor('const_tensor', TensorProto.FLOAT, [1, 2], [0.1, 0.9])
    )
    graph = helper.make_graph([const_node], 'dummy_graph', [input_ids], [logits])
    model = helper.make_model(
        graph,
        producer_name='test',
        ir_version=8,
        opset_imports=[helper.make_opsetid("", 17)]
    )
    model_path = tmp_path / "model.onnx"
    onnx.save(model, str(model_path))

    sess, info = create_session(model_path, mode="cpu", cache_dir=tmp_path / "c", fp16=False)
    assert info.requested == "cpu"
    assert sess is not None


def test_snapdragon_accelerator_invalid_file(tmp_path):
    # SnapdragonNPUAccelerator with non-existent model path handles exception gracefully
    non_existent = tmp_path / "non_existent.onnx"
    acc = SnapdragonNPUAccelerator(onnx_model_path=str(non_existent), mode="cpu")
    assert acc.session is None
    res = acc.run_npu_inference(None)
    assert "active_provider" in res


def test_extra_agent_and_ml_coverage():
    from backend.app.ml.sentiment_engine import SentimentEngine
    se = SentimentEngine()
    res = se.analyze_sentiment("This is a fantastic product!")
    assert "label" in res








