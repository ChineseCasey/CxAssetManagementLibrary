@echo off
setlocal
cd /d "%~dp0"

echo Cleaning generated files...

for /d /r %%d in (__pycache__) do (
  if exist "%%d" rd /s /q "%%d"
)

for /r %%f in (*.pyc) do (
  if exist "%%f" del /f /q "%%f"
)

if exist "frontend\dist" rd /s /q "frontend\dist"
if exist "frontend\node_modules\.vite" rd /s /q "frontend\node_modules\.vite"
if exist "logs" rd /s /q "logs"
if exist ".pytest_cache" rd /s /q ".pytest_cache"

echo Done.
