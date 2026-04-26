@echo off
setlocal
cd /d "%~dp0"

set "SHOW_CONSOLE=%~1"
if "%SHOW_CONSOLE%"=="" set "SHOW_CONSOLE=0"

if not exist "run_desktop.py" (
  echo Desktop entry not found.
  exit /b 1
)

if not exist "logs" mkdir "logs"

if "%SHOW_CONSOLE%"=="1" (
  start "CxAsset Desktop" /D "%~dp0" cmd /k "timeout /t 3 /nobreak >nul & python run_desktop.py"
) else (
  start "CxAsset Desktop" /D "%~dp0" pythonw run_desktop.py
)

echo Desktop started. show_console=%SHOW_CONSOLE%
