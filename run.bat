@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set PYTHONPATH=
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" "app.py"
) else (
    start "" pythonw "app.py"
)
