@echo off
setlocal
cd /d "%~dp0"

set "PY=python"
where python >nul 2>nul
if errorlevel 1 set "PY=py -3"

if not exist ".venv\Scripts\python.exe" (
    echo [Folio] Creating virtual environment...
    %PY% -m venv .venv
    if errorlevel 1 goto :error
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :error
)

echo.
echo [Folio] Starting at http://127.0.0.1:5000
echo.
".venv\Scripts\python.exe" app.py
goto :eof

:error
echo.
echo [Folio] Setup failed. Install Python 3.10+ and try again.
pause