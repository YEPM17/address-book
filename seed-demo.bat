@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [Folio] Run run.bat once to create the environment first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m flask --app app seed-demo