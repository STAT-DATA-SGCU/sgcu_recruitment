@echo off
chcp 65001 > nul
echo ========================================================
echo   SGCU Recruitment Data Analytics Dashboard
echo   องค์การบริหารสโมสรนิสิตจุฬาฯ (รอบที่ 1 - 4)
echo ========================================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Creating Python Virtual Environment (.venv)...
    python -m venv .venv
    echo [INFO] Installing requirements...
    .\.venv\Scripts\pip install -r requirements.txt
)

echo [INFO] Launching Streamlit Dashboard...
echo [INFO] Press Ctrl+C in this window to stop the dashboard.
echo.
.\.venv\Scripts\python -m streamlit run app.py
pause

