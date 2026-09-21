# RitaDrishti-AI — Qualcomm Snapdragon NPU Architecture & QNN Integration Blueprint

## 1. Overview
RitaDrishti-AI provides an **on-device ONNX / QNN execution engine** for local neural network inference on **Qualcomm Snapdragon X Elite / X Plus Copilot+ PCs** via `QNNExecutionProvider` (targeting the Qualcomm Hexagon Tensor Processor / HTP).

**Status**: *Experimental — QNN implementation available, hardware validation pending until real Snapdragon results are committed.*

---

## 2. Architecture & QNN Hardware Acceleration Flow

```text
Input Review Text
       │
  `load_encoder` (Fast Tokenizer -> static int64 tensors: input_ids[1, 128], attention_mask[1, 128])
       │
  `create_session` (probes ONNX Runtime providers)
       ├─> Primary: `QNNExecutionProvider` (Hexagon NPU / HTP, FP16 & QDQ INT8)
       └─> Fallback: `CPUExecutionProvider` (Clean fallback read directly from session.get_providers())
```

---

## 3. Static Shape Export for QNN HTP Backend

Qualcomm Hexagon NPU works best with static tensor shapes:

```python
import torch
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("models/review_transformer")
dummy_ids = torch.ones((1, 128), dtype=torch.int64)
dummy_mask = torch.ones((1, 128), dtype=torch.int64)

torch.onnx.export(
    model,
    (dummy_ids, dummy_mask),
    "model.fp32.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    opset_version=17
)
```

---

## 4. Native Snapdragon PC Deployment

Run the native PowerShell scripts on a Windows ARM64 Snapdragon PC:

```powershell
# 1. Environment & model bundle setup
.\scripts\setup_snapdragon.ps1

# 2. Launch FastAPI with NPU acceleration
.\scripts\run_snapdragon.ps1
```
