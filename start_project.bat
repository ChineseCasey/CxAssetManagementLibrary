@echo off
setlocal

cd /d "%~dp0"

echo [1/4] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed or not in PATH.
  pause
  exit /b 1
)

echo [2/4] Installing backend dependencies...
python -m pip install -e .
if errorlevel 1 (
  echo Failed to install backend dependencies.
  pause
  exit /b 1
)

echo [3/4] Applying database migrations...
python -m alembic upgrade head
if errorlevel 1 (
  echo Failed to apply migrations.
  pause
  exit /b 1
)

if exist "frontend\package.json" (
  echo [4/4] Preparing frontend dependencies...
  if not exist "frontend\node_modules" (
    call npm --prefix frontend install
    if errorlevel 1 (
      echo Failed to install frontend dependencies.
      pause
      exit /b 1
    )
  )
)

echo Starting backend and frontend...
start "CxAsset API" cmd /k "cd /d \"%~dp0\" && python -m uvicorn cxasset_api.main:app --app-dir src --host 127.0.0.1 --port 8000 --reload"

if exist "frontend\package.json" (
  start "CxAsset Frontend" cmd /k "cd /d \"%~dp0frontend\" && npm run dev -- --host 127.0.0.1 --port 5173"
) else (
  echo Frontend not found, started backend only.
)

echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo.
echo Press any key to close this launcher window...
pause >nul
