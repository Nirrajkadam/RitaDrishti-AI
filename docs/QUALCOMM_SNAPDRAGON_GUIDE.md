# RitaDrishti-AI — Qualcomm Snapdragon AI Hub & NPU Optimization Blueprint (Experimental)

## 1. Overview
RitaDrishti-AI includes an experimental optimization blueprint for executing sentiment models locally on **Qualcomm Snapdragon X Elite and X Plus Copilot+ PCs** using DirectML / QNN.

*Note: In the core RitaDrishti-AI platform, NPU execution is feature-gated via `ENABLE_NPU=false` in `backend/app/config.py`.*

---

## 2. Technical Optimization Steps

### Step 1: Export PyTorch Models to ONNX Format
Export DistilBERT sentiment models using PyTorch ONNX exporter:

```python
import torch
from transformers import DistilBertForSequenceClassification

model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
dummy_input = torch.randint(0, 1000, (1, 128)) # Batch size 1, sequence length 128

torch.onnx.export(
    model,
    dummy_input,
    "sentiment_model.onnx",
    input_names=["input_ids"],
    output_names=["logits"],
    dynamic_axes={"input_ids": {0: "batch_size", 1: "sequence_length"}},
    opset_version=17
)
```

### Step 2: Configure ONNX Runtime for DirectML / Qualcomm QNN
In Windows 11 Copilot+ PCs (ARM64), configure ONNX Runtime to target DirectML (`DmlExecutionProvider`) or Qualcomm Neural Processing SDK (`QNNExecutionProvider`):

```python
import onnxruntime as ort

options = ort.SessionOptions()
options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# Target Qualcomm Hexagon NPU Execution Provider
session = ort.InferenceSession(
    "sentiment_model.onnx",
    providers=["DmlExecutionProvider", "QNNExecutionProvider", "CPUExecutionProvider"],
    sess_options=options
)
```
