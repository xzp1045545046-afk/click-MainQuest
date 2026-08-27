@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set PYTHONPATH=
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" "app.py"
) else (
    python "app.py"
)
pause
