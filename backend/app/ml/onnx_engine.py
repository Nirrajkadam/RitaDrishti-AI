"""On-device fake-review scoring with a (quantized) transformer via ONNX Runtime.

A deployable model directory contains:
    model.qdq.onnx   quantized model for the NPU   (preferred)
    model.fp32.onnx  float model                   (fallback / baseline)
    tokenizer.json   fast-tokenizer definition

Inputs are padded to a fixed length because the HTP backend works best with
static shapes. Reviews are scored one at a time (batch size 1).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

try:  # package import (inside the FastAPI app)
    from .accelerator import AcceleratorInfo, create_session
except ImportError:  # script import (benchmarks / scripts add this folder to sys.path)
    from accelerator import AcceleratorInfo, create_session

log = logging.getLogger(__name__)

Encoder = Callable[[str], tuple[np.ndarray, np.ndarray]]


def load_encoder(model_dir: str | Path, max_len: int = 128) -> Encoder:
    """Return ``encode(text) -> (input_ids[1, L], attention_mask[1, L])`` as int64."""
    model_dir = Path(model_dir)
    tok_file = model_dir / "tokenizer.json"
    if tok_file.exists():
        try:
            from tokenizers import Tokenizer

            tok = Tokenizer.from_file(str(tok_file))
            pad_id = tok.token_to_id("[PAD]")
            tok.enable_truncation(max_length=max_len)
            tok.enable_padding(
                length=max_len, pad_id=0 if pad_id is None else pad_id, pad_token="[PAD]"
            )

            def encode(text: str):
                enc = tok.encode(text)
                return (
                    np.asarray([enc.ids], dtype=np.int64),
                    np.asarray([enc.attention_mask], dtype=np.int64),
                )

            return encode
        except Exception as err:
            log.warning("Failed to load fast tokenizer from %s: %s", tok_file, err)

    try:
        from transformers import AutoTokenizer  # heavier fallback

        hf = AutoTokenizer.from_pretrained(model_dir)

        def encode(text: str):
            out = hf(text, truncation=True, padding="max_length", max_length=max_len,
                     return_tensors="np")
            return out["input_ids"].astype(np.int64), out["attention_mask"].astype(np.int64)

        return encode
    except Exception:
        pass

    raise FileNotFoundError(
        f"Tokenizer definition could not be loaded from {model_dir}. "
        "Ensure tokenizer.json is present in the model directory or HuggingFace transformers is installed."
    )


def _softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


class OnnxReviewEngine:
    """Scores review text. ``predict_proba`` returns P(fake) in [0, 1] per review."""

    def __init__(
        self,
        model_dir: str | Path,
        *,
        mode: str | None = None,
        max_len: int = 128,
        fake_label_index: int = 1,
        cache_dir: str | Path | None = None,
    ) -> None:
        model_dir = Path(model_dir)
        model_file = next(
            (model_dir / n for n in ("model.qdq.onnx", "model.fp32.onnx")
             if (model_dir / n).exists()),
            None,
        )
        if model_file is None:
            raise FileNotFoundError(
                f"No model.qdq.onnx / model.fp32.onnx in {model_dir}. "
                "Run scripts/export_quantize.py first."
            )
        self.model_file = model_file
        self.fake_label_index = fake_label_index
        self._encode = load_encoder(model_dir, max_len)
        self._session, self.info = create_session(model_file, mode, cache_dir=cache_dir)
        self._input_names = {i.name for i in self._session.get_inputs()}
        self.predict_proba(["warm-up"])  # first run triggers backend graph preparation

    @property
    def info_dict(self) -> dict:
        return {"model": self.model_file.name, **self.info.as_dict()}

    def _logits(self, text: str) -> np.ndarray:
        ids, mask = self._encode(text)
        feed = {"input_ids": ids, "attention_mask": mask}
        feed = {k: v for k, v in feed.items() if k in self._input_names}
        return self._session.run(None, feed)[0]

    def predict_proba(self, texts: Sequence[str]) -> list[float]:
        probs = [_softmax(self._logits(t))[0, self.fake_label_index] for t in texts]
        return [float(p) for p in probs]

    def score(self, text: str) -> dict:
        p = self.predict_proba([text])[0]
        return {
            "fake_probability": p,
            "label": "likely_fake" if p >= 0.5 else "likely_genuine",
            "accelerator": self.info.label,
        }
