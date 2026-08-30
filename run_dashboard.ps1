# SGCU Recruitment Dashboard PowerShell Runner
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  SGCU Recruitment Data Analytics Dashboard" -ForegroundColor Green
Write-Host "  องค์การบริหารสโมสรนิสิตจุฬาฯ (รอบที่ 1 - 4)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "[INFO] Creating Python Virtual Environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[INFO] Installing requirements..." -ForegroundColor Yellow
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host "[INFO] Starting Streamlit Dashboard..." -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -m streamlit run app.py

