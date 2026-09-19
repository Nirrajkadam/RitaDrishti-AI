"""
Unit tests for Snapdragon NPU accelerator module
"""

import pytest
import numpy as np
from backend.app.ml.snapdragon_opt import SnapdragonNPUAccelerator


def test_snapdragon_npu_inference():
    accelerator = SnapdragonNPUAccelerator()
    dummy_input = np.random.randn(8, 384).astype(np.float32)
    res = accelerator.run_npu_inference(dummy_input)

    assert "execution_provider" in res
    assert "latency_ms" in res
    assert res["output_shape"] == [8, 128]


def test_snapdragon_benchmark():
    accelerator = SnapdragonNPUAccelerator()
    bench = accelerator.benchmark_cpu_vs_npu(iterations=5)

    assert bench["iterations"] == 5
    assert "avg_latency_ms" in bench
    assert "estimated_npu_speedup" in bench
