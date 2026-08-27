@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set PYTHONPATH=

set "PYW="
if exist "venv\Scripts\pythonw.exe" (
    set "PYW=venv\Scripts\pythonw.exe"
) else if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\pythonw.exe" (
    set "PYW=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\pythonw.exe"
) else (
    for /f "delims=" %%i in ('where pythonw 2^>nul') do (
        set "PYW=%%i"
        goto :found
    )
)

:found
if defined PYW (
    start "" "%PYW%" "app.py"
) else (
    echo Error: 找不到 pythonw.exe，请确保 Python 已安装并加入 PATH，或创建 venv。
    pause
)
