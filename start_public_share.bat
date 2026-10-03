@echo off
title CycloneGuard - 24/7 Permanent Cloud Platform
echo =========================================================================
echo            CYCLONEGUARD - 24/7 PERMANENT CLOUD PLATFORM
echo =========================================================================
echo.
echo  The CycloneGuard platform is permanently live and running in the cloud:
echo.
echo    PERMANENT 24/7 URL : https://cycloneguard-web.onrender.com
echo    GUIDED JUDGE DEMO  : https://cycloneguard-web.onrender.com/demo
echo    BACKEND API        : https://cycloneguard-api.onrender.com/api/v1/health
echo.
echo  No local servers or tunnels are needed. The website is active 24/7.
echo =========================================================================
echo.
set /p OPEN_BROWSER="Would you like to open the live website now? (Y/N): "
if /i "%OPEN_BROWSER%"=="Y" (
    start https://cycloneguard-web.onrender.com
)
echo.
pause
