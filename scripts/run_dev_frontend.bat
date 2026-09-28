@echo off
REM Start CycloneGuard Next.js frontend
cd /d "%~dp0\..\frontend"
echo Starting CycloneGuard Next.js Frontend Server on port 3000...
npm.cmd run dev -- --port 3000
