# RitaDrishti-AI — Native Snapdragon PC Server Runner
# Launches FastAPI backend server with ACCELERATOR=npu and ENABLE_NPU=true

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " RitaDrishti-AI: Starting Server with Snapdragon NPU" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

$env:ACCELERATOR = "npu"
$env:ENABLE_NPU = "true"
$env:APP_ENV = "development"

Write-Host "[INFO] ACCELERATOR = $env:ACCELERATOR" -ForegroundColor Yellow
Write-Host "[INFO] ENABLE_NPU  = $env:ENABLE_NPU" -ForegroundColor Yellow

# Verify model artifacts exist
if (-not (Test-Path "backend/app/ml/artifacts/onnx/model.qdq.onnx") -and -not (Test-Path "backend/app/ml/artifacts/onnx/model.fp32.onnx")) {
    Write-Host "[NOTICE] ONNX model artifacts missing. Running export_quantize.py..." -ForegroundColor Yellow
    .\venv\Scripts\python.exe scripts/export_quantize.py --model-dir backend/app/ml/artifacts/onnx
}

Write-Host "[INFO] Starting FastAPI server on http://localhost:8000 ..." -ForegroundColor Green
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
