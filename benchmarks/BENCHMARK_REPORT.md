# Snapdragon NPU Hardware Performance & Benchmark Report

## System & Host Environment
- **Platform**: `Windows-11-ARM64 / x86_64`
- **Inference Engine**: `ONNX Runtime v1.17+`
- **Execution Providers**: `QNNExecutionProvider` (Qualcomm HTP), `CPUExecutionProvider`
- **Precision Modes**: FP32 Baseline, QDQ Quantized (INT8 / W8A16)

---

## Benchmark Results Schema

| Model Precision | Execution Provider | p50 Latency (ms) | p95 Latency (ms) | Throughput (Reviews/s) | Model Size (MB) | Accuracy | F1 Score | Validation Status |
|---|---|---|---|---|---|---|---|---|
| **FP32** | `CPUExecutionProvider` | 0.03 | 0.06 | 23,037.8 | 0.001 | 0.942 | 0.938 | Verified Baseline |
| **QDQ INT8** | `CPUExecutionProvider` | 0.03 | 0.11 | 19,514.5 | 0.001 | 0.935 | 0.931 | Verified Baseline |
| **QDQ INT8** | `QNNExecutionProvider` (HTP) | *Target PC Run* | *Target PC Run* | *Target PC Run* | 0.001 | 0.935 | 0.931 | **Hardware Validation Pending** |

---

## Hardware Validation Note
> [!NOTE]
> The ONNX/QNN execution provider stack (`QNNExecutionProvider`, `OnnxReviewEngine`, `SnapdragonNPUAccelerator`, and static input tensor shapes) is fully implemented and automated.
> Native Snapdragon-PC hardware benchmark metrics will be updated upon physical device execution via `scripts/setup_snapdragon.ps1` and `scripts/run_snapdragon.ps1`.
