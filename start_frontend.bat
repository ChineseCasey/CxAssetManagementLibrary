@echo off
setlocal
cd /d "%~dp0"

set "SHOW_CONSOLE=%~1"
if "%SHOW_CONSOLE%"=="" set "SHOW_CONSOLE=0"

if not exist "frontend\package.json" (
  echo Frontend not found.
  exit /b 1
)

if not exist "logs" mkdir "logs"

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":5173 .*LISTENING"') do taskkill /PID %%p /F >nul 2>nul

if "%SHOW_CONSOLE%"=="1" (
  start "CxAsset Frontend" /D "%~dp0frontend" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -WorkingDirectory '%~dp0frontend' -ArgumentList @('/c','npm run dev -- --host 127.0.0.1 --port 5173') -WindowStyle Hidden -RedirectStandardOutput '%~dp0logs\frontend.log' -RedirectStandardError '%~dp0logs\frontend.err.log'"
)

echo Frontend started. show_console=%SHOW_CONSOLE%
