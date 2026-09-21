# RitaDrishti-AI — Native Snapdragon PC Environment Setup Script
# Run on Windows 11 ARM64 (Qualcomm Snapdragon X Elite / Plus devices)

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " RitaDrishti-AI: Snapdragon NPU Setup (Windows ARM64)" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Check Python Architecture
$pythonArch = & python -c "import platform; print(platform.machine())"
Write-Host "[INFO] Detected Python Architecture: $pythonArch" -ForegroundColor Yellow

if ($pythonArch -ne "ARM64" -and $pythonArch -ne "aarch64") {
    Write-Host "[WARNING] Python is running under x64 emulation on Windows ARM64." -ForegroundColor Yellow
    Write-Host "[WARNING] For maximum Qualcomm Hexagon NPU performance, install native ARM64 Python." -ForegroundColor Yellow
}

# 2. Create Virtual Environment
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating Virtual Environment (venv)..." -ForegroundColor Green
    python -m venv venv
}

# 3. Install Dependencies
Write-Host "[INFO] Upgrading pip and installing requirements..." -ForegroundColor Green
.\venv\Scripts\python.exe -m pip install --upgrade pip

if ($pythonArch -eq "ARM64" -or $pythonArch -eq "aarch64") {
    Write-Host "[INFO] Installing native onnxruntime-qnn for Snapdragon NPU..." -ForegroundColor Green
    .\venv\Scripts\python.exe -m pip install onnxruntime-qnn -r requirements.txt
} else {
    Write-Host "[INFO] Installing onnxruntime..." -ForegroundColor Green
    .\venv\Scripts\python.exe -m pip install -r requirements-test.txt
}

# 4. Generate ONNX Model Artifacts
Write-Host "[INFO] Exporting static-shape ONNX models for QNN NPU..." -ForegroundColor Green
.\venv\Scripts\python.exe scripts/export_quantize.py --model-dir backend/app/ml/artifacts/onnx

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Setup Complete! Run scripts/run_snapdragon.ps1 to start." -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
