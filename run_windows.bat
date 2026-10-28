@echo off
title TechXfluence AI
cd /d "%~dp0"
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 ( echo Install Python and tick "Add to PATH". & pause & exit /b 1 )
)
call .venv\Scripts\python.exe -m pip install -q -r requirements.txt
if errorlevel 1 ( echo Package install failed. Check internet. & pause & exit /b 1 )
if "%GEMINI_API_KEY%"=="" if not exist .streamlit\secrets.toml (
  echo [WARNING] GEMINI_API_KEY not set. Copy .streamlit\secrets.toml.example to .streamlit\secrets.toml and add your free key.
)
echo Opening http://localhost:8501  (Ctrl+C to stop)
call .venv\Scripts\python.exe -m streamlit run app.py
pause
