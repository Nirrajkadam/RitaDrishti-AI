"""ONNX Runtime accelerator selection: Snapdragon NPU (QNN / HTP) with safe CPU fallback.

Design rules
------------
* The *active* provider is read back from the created session, never assumed.
  ONNX Runtime can fall back to CPU without raising, so anything shown in the UI,
  /health or the benchmark comes from ``session.get_providers()``.
* ``ACCELERATOR`` env var: ``auto`` (default) | ``npu`` (fail loudly if unavailable) | ``cpu``.
* Optional context cache: the first NPU run compiles the model for the HTP backend
  (slow); the compiled context is stored and reused on later starts.
"""
from __future__ import annotations

import logging
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import onnxruntime as ort

log = logging.getLogger(__name__)

QNN_EP = "QNNExecutionProvider"
CPU_EP = "CPUExecutionProvider"
VALID_MODES = ("auto", "npu", "cpu")


@dataclass(frozen=True)
class AcceleratorInfo:
    requested: str
    active_providers: tuple[str, ...]
    npu_active: bool
    label: str
    note: str | None = None

    def as_dict(self) -> dict:
        data = asdict(self)
        data["active_providers"] = list(self.active_providers)
        return data


def qnn_available() -> bool:
    """True if this onnxruntime build ships the QNN execution provider."""
    return QNN_EP in ort.get_available_providers()


def _qnn_backend() -> str:
    return "QnnHtp.dll" if sys.platform == "win32" else "libQnnHtp.so"


def create_session(
    model_path: str | Path,
    mode: str | None = None,
    *,
    cache_dir: str | Path | None = None,
    perf_mode: str = "burst",
    fp16: bool = True,
) -> tuple[ort.InferenceSession, AcceleratorInfo]:
    """Create an InferenceSession on the best available backend.

    Args:
        model_path: ONNX model (static input shapes recommended for the NPU).
        mode: ``auto`` | ``npu`` | ``cpu``. Defaults to the ACCELERATOR env var.
        cache_dir: if set, compiled QNN context is cached here between runs.
        perf_mode: HTP performance mode (``burst``, ``high_performance``, ``balanced`` ...).
        fp16: let the HTP run float models in FP16 (only affects non-quantized models).
    """
    mode = (mode or os.getenv("ACCELERATOR", "auto")).strip().lower()
    if mode not in VALID_MODES:
        raise ValueError(f"ACCELERATOR must be one of {VALID_MODES}, got {mode!r}")

    model_path = Path(model_path)
    note: str | None = None
    providers: list = [CPU_EP]
    load_path = model_path
    so = ort.SessionOptions()
    so.log_severity_level = 3

    if mode != "cpu":
        if qnn_available():
            qnn_opts = {
                "backend_path": _qnn_backend(),
                "htp_performance_mode": perf_mode,
                "enable_htp_fp16_precision": "1" if fp16 else "0",
            }
            providers = [(QNN_EP, qnn_opts), CPU_EP]
            if cache_dir:
                cache = Path(cache_dir)
                cache.mkdir(parents=True, exist_ok=True)
                ctx = cache / f"{model_path.stem}_ctx.onnx"
                if ctx.exists():
                    load_path = ctx
                else:
                    so.add_session_config_entry("ep.context_enable", "1")
                    so.add_session_config_entry("ep.context_file_path", str(ctx))
        elif mode == "npu":
            raise RuntimeError(
                "ACCELERATOR=npu but QNNExecutionProvider is not available in this "
                "onnxruntime build. On Windows on Arm install `onnxruntime-qnn` with "
                "native ARM64 Python."
            )
        else:
            note = "QNN execution provider not available; using CPU"

    try:
        session = ort.InferenceSession(str(load_path), sess_options=so, providers=providers)
    except Exception as exc:  # provider/driver/model incompatibility
        if mode == "npu":
            raise
        log.warning("NPU session failed (%s); falling back to CPU", exc)
        note = f"NPU session failed, fell back to CPU: {str(exc)[:160]}"
        session = ort.InferenceSession(
            str(model_path), sess_options=ort.SessionOptions(), providers=[CPU_EP]
        )

    active = tuple(session.get_providers())
    npu = QNN_EP in active
    info = AcceleratorInfo(
        requested=mode,
        active_providers=active,
        npu_active=npu,
        label="Snapdragon NPU (QNN/HTP)" if npu else "CPU",
        note=note,
    )
    log.info("Inference backend: %s (%s)", info.label, ", ".join(active))
    return session, info
