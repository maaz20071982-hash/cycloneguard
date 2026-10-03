@echo off
title CycloneGuard - Public Access Launcher
echo =========================================================================
echo            CYCLONEGUARD - MULTI-DEVICE PUBLIC ACCESS LAUNCHER
echo =========================================================================
echo.
echo  [1/3] Starting CycloneGuard Backend (FastAPI :8000)...
if exist "venv\Scripts\activate.bat" (
    start "CycloneGuard Backend" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --app-dir backend --port 8000 --host 0.0.0.0"
) else (
    start "CycloneGuard Backend" cmd /k "python -m uvicorn app.main:app --app-dir backend --port 8000 --host 0.0.0.0"
)

echo  [2/3] Starting CycloneGuard Frontend (Next.js :3000)...
start "CycloneGuard Frontend" cmd /k "cd frontend && npm.cmd run dev"

echo.
echo  Waiting 6 seconds for local servers to initialize...
timeout /t 6 >nul

echo  [3/3] Opening Secure Cloudflare HTTPS Tunnel for Mobile & Remote Devices...
echo.
echo  Look at the Cloudflare window to find your unique https://*.trycloudflare.com link.
echo  You can open that link on your smartphone, tablet, or any remote browser!
echo.
start "CycloneGuard Cloudflare Public Tunnel" cmd /k "cloudflared.exe tunnel --url http://localhost:3000"

echo =========================================================================
echo  All services are running! Press any key to close this launcher.
echo =========================================================================
pause
