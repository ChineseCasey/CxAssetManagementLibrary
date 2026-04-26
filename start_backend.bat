@echo off
setlocal
cd /d "%~dp0"

set "SHOW_CONSOLE=%~1"
if "%SHOW_CONSOLE%"=="" set "SHOW_CONSOLE=0"

if not exist "logs" mkdir "logs"

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":8000 .*LISTENING"') do taskkill /PID %%p /F >nul 2>nul

if "%SHOW_CONSOLE%"=="1" (
  start "CxAsset API" /D "%~dp0" cmd /k "python -m uvicorn cxasset_api.main:app --app-dir src --host 127.0.0.1 --port 8000"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'python' -WorkingDirectory '%~dp0' -ArgumentList @('-m','uvicorn','cxasset_api.main:app','--app-dir','src','--host','127.0.0.1','--port','8000') -WindowStyle Hidden -RedirectStandardOutput '%~dp0logs\backend.log' -RedirectStandardError '%~dp0logs\backend.err.log'"
)

echo Backend started. show_console=%SHOW_CONSOLE%
