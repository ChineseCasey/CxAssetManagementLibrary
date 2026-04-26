@echo off
setlocal

cd /d "%~dp0"

rem =========================
rem Launch options
rem =========================
rem 1 = show per-service console windows
rem 0 = run services hidden (logs written to .\logs\*.log)
set "SHOW_SERVICE_CONSOLES=0"

rem 1 = auto install/check dependencies before start
rem 0 = skip dependency preparation and just launch
set "PREPARE_DEPENDENCIES=1"

rem Select which services to launch in one-click mode
set "START_BACKEND=1"
set "START_FRONTEND=1"
set "START_DESKTOP=1"

if not exist "logs" mkdir "logs"
if not exist "data" mkdir "data"
if exist "cxasset.db" (
  if not exist "data\cxasset.db" (
    echo [db] Migrating database: .\cxasset.db -> .\data\cxasset.db
    move /Y "cxasset.db" "data\cxasset.db" >nul
  )
)

if "%PREPARE_DEPENDENCIES%"=="1" echo [1/6] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed or not in PATH.
  pause
  exit /b 1
)

if "%PREPARE_DEPENDENCIES%"=="1" (
  echo [2/6] Installing backend dependencies...
  python -m pip install -e .
  if errorlevel 1 (
    echo Failed to install backend dependencies.
    pause
    exit /b 1
  )

  echo [3/6] Applying database migrations...
  python -m alembic upgrade head
  if errorlevel 1 (
    echo Failed to apply migrations.
    pause
    exit /b 1
  )
)

if exist "frontend\package.json" (
  if "%PREPARE_DEPENDENCIES%"=="1" (
    echo [4/6] Preparing frontend dependencies...
    where npm >nul 2>nul
    if errorlevel 1 (
      echo npm is not installed or not in PATH.
      pause
      exit /b 1
    )
    if not exist "frontend\node_modules" (
      call npm --prefix frontend install
      if errorlevel 1 (
        echo Failed to install frontend dependencies.
        pause
        exit /b 1
      )
    )
  )
)

if "%PREPARE_DEPENDENCIES%"=="1" (
  echo [5/6] Preparing desktop dependencies...
  python -c "import PySide6, requests, singledispatch, dayu_path" >nul 2>nul
  if errorlevel 1 (
    python -m pip install -r requirements-desktop.txt
    if errorlevel 1 (
      echo Failed to install desktop dependencies.
      pause
      exit /b 1
    )
  )
)

if not exist "third_party\dayu_widgets" (
  if "%PREPARE_DEPENDENCIES%"=="1" (
    if not exist "third_party" mkdir "third_party"
    git clone https://github.com/ChineseCasey/dayu_widgets.git "third_party/dayu_widgets"
    if errorlevel 1 (
      echo Failed to clone dayu_widgets.
      pause
      exit /b 1
    )
  )
)

echo [6/6] Starting backend, frontend and desktop...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":8000 .*LISTENING"') do taskkill /PID %%p /F >nul 2>nul
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":5173 .*LISTENING"') do taskkill /PID %%p /F >nul 2>nul

if "%START_BACKEND%"=="1" (
  call "%~dp0start_backend.bat" %SHOW_SERVICE_CONSOLES%
)
if "%START_FRONTEND%"=="1" (
  call "%~dp0start_frontend.bat" %SHOW_SERVICE_CONSOLES%
)
if "%START_DESKTOP%"=="1" (
  call "%~dp0start_desktop.bat" %SHOW_SERVICE_CONSOLES%
)

echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo Desktop:  Python UI window
echo.
echo Press any key to close this launcher window...
pause >nul
