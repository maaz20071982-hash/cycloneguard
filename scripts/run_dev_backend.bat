@echo off
REM Start CycloneGuard FastAPI backend
cd /d "%~dp0\.."
echo Starting CycloneGuard Backend Server on port 8000...
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
