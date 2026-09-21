# Snapdragon NPU path: setup, integration, verification

**Pitch:** RitaDrishti-AI scores review authenticity **on-device**. PII is redacted locally, a
quantized transformer runs on the Snapdragon NPU, and review text never leaves the laptop.

## 0. What this kit adds

| File | Purpose |
|---|---|
| `backend/app/ml/accelerator.py` | Picks NPU (QNN/HTP) or CPU; reports the backend that is *actually* active |
| `backend/app/ml/onnx_engine.py` | `OnnxReviewEngine`: tokenizer + ONNX session + `predict_proba` |
| `scripts/finetune_transformer.py` | Fine-tune DistilBERT (or any small BERT) on your `text,label` CSV |
| `scripts/export_quantize.py` | Static-shape ONNX export, parity check, QNN QDQ quantization |
| `benchmarks/run_benchmark.py` | FP32 vs QDQ, CPU vs NPU: latency, throughput, size, accuracy, F1 |
| `requirements-npu.txt` / `requirements-train.txt` | Deploy-side and train-side dependencies |

Status: the engine, session selection and benchmark were smoke-tested with a stand-in model on CPU.
The fine-tune and export/quantize scripts are syntax-checked only. **Nothing here has been run on
Snapdragon hardware yet**; do not publish NPU numbers until you have measured them.

## 1. Train and export (x64 GPU machine or Colab)

```bash
pip install -r requirements-train.txt
python scripts/finetune_transformer.py --data data/reviews.csv --out models/review_transformer
python scripts/export_quantize.py --model-dir models/review_transformer          # W8A16 (default)
python scripts/export_quantize.py --model-dir models/review_transformer --act-bits 8   # compare
```

Copy `models/review_transformer/` to the Snapdragon PC.

## 2. Run on the Snapdragon PC

```powershell
# native ARM64 Python 3.11+ (check: python -c "import platform; print(platform.machine())"  -> ARM64)
python -m venv venv; .\venv\Scripts\activate
pip install -r requirements-npu.txt
python -c "import onnxruntime as o; print(o.get_available_providers())"    # must list QNNExecutionProvider
python benchmarks/run_benchmark.py --model-dir models/review_transformer --data models/review_transformer/val.csv
```

## 3. Wire it into the API

I have not seen your `FakeReviewEngine` interface, so adapt method names to match it.

```python
# backend/app/ml/transformer_engine.py
from app.config import settings
from app.ml.onnx_engine import OnnxReviewEngine

class TransformerFakeReviewEngine:
    def __init__(self) -> None:
        self._engine = OnnxReviewEngine(settings.MODEL_DIR, cache_dir=settings.NPU_CACHE_DIR)

    def predict(self, text: str) -> float:            # match FakeReviewEngine's signature
        return self._engine.predict_proba([text])[0]

    @property
    def accelerator(self) -> dict:
        return self._engine.info_dict
```

Config (`backend/app/config.py` / `.env.example`), replacing the boolean `ENABLE_NPU`:

```
ACCELERATOR=auto              # auto | npu | cpu
MODEL_DIR=models/review_transformer
NPU_CACHE_DIR=.cache/qnn      # optional: reuse compiled NPU context between starts
```

Expose the truth so judges (and your demo video) can see it:

```python
@router.get("/health")
def health():
    return {"status": "ok", "accelerator": review_engine.accelerator}
```

Show `accelerator.label` as a badge in the Next.js UI and Streamlit dashboard, for example
"Running on: Snapdragon NPU (QNN/HTP)".

## 4. Verify the NPU is really being used

`get_providers()` listing QNN proves the provider loaded, not that every operator runs on it. ONNX
Runtime can assign unsupported operators to CPU. So:

1. Run the benchmark and watch **Task Manager -> Performance -> NPU** while it runs. It should spike.
2. Compare NPU latency to CPU latency. An NPU row no faster than CPU suggests heavy fallback.
3. Record what you observe (screenshot or screen recording) for the demo.

## 5. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `QNNExecutionProvider` missing | x64 Python or plain `onnxruntime`. Install ARM64 Python and `onnxruntime-qnn` |
| Session creation fails on NPU | Dynamic shapes or unsupported ops. Keep static `[1, max_len]`; try `--act-bits 16` or run the FP32 model with `fp16=True` |
| F1 drops after quantization | Use W8A16 instead of W8A8; raise `--calib-n`; make calibration data representative; or ship FP32 on the NPU in FP16 |
| First start is slow | HTP graph compilation. Set `NPU_CACHE_DIR` so later starts reuse the compiled context |
| Numbers vary between runs | Increase `--iters`, close background apps, plug in power, keep the same `htp_performance_mode` |
| Ops fall back silently | Expected for some ops; report honestly in the README rather than hiding it |

## 6. README hero block (fill with measured values only)

```markdown
### Private, on-device review trust scoring for Snapdragon PCs
Reviews are PII-redacted and scored **locally** by a quantized transformer on the Snapdragon NPU. No cloud calls.

| Model | Backend | p50 latency | Reviews/s | Size | F1 |
|---|---|---|---|---|---|
| FP32 | CPU | _measure_ | _measure_ | _measure_ | _measure_ |
| QDQ (W8A16) | Snapdragon NPU | _measure_ | _measure_ | _measure_ | _measure_ |

Measured on: <exact laptop model, Snapdragon chip, RAM, Windows build, onnxruntime-qnn version>.
```

## 7. Demo video shot list (2 to 3 minutes)

1. Problem and one-line pitch (10 s)
2. Wi-Fi off, paste a fake and a genuine review, show scores and the NPU badge (60 s)
3. Task Manager NPU graph spiking during the benchmark, then the results table (40 s)
4. Architecture diagram: PII redaction -> NPU inference -> DB -> dashboard, on-device boundary marked (30 s)
5. What is next (15 s)

## 8. Definition of done before you submit

- [ ] `ACCELERATOR=auto` selects the NPU on a Snapdragon machine, with a CPU fallback elsewhere
- [ ] `/health` reports the active backend; UI shows it
- [ ] Benchmark table in the README contains only numbers you measured, with hardware details
- [ ] F1 reported for FP32 and quantized; dataset and split described
- [ ] CrewAI, Qdrant and Ollama either work end to end or are moved to a "Roadmap" section
- [ ] One compose file; native install script documented as the primary path
- [ ] Commit history and a CHANGELOG show what was added during the Submission Period
- [ ] Secrets scan of the git history; README, docs and video in English
- [ ] Intake form checked twice (submission cannot be edited afterwards; one submission only)
