@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set PYTHONPATH=

set "PY="
if exist "venv\Scripts\python.exe" (
    set "PY=venv\Scripts\python.exe"
) else if exist "%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe" (
    set "PY=%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
) else (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        set "PY=%%i"
        goto :found
    )
)

:found
if not defined PY (
    echo Error: 找不到 python.exe，请确保 Python 已安装并加入 PATH，或创建 venv。
    echo 你也可以运行：python -m venv venv
    echo      然后：venv\Scripts\pip install pywebview
    pause
    exit /b 1
)

REM 确保本地同步服务（8765）在线，桌面版需经 http origin 加载才能用云同步
netstat -ano | findstr ":8765" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    start "" "%PY%" "server.py"
    timeout /t 2 /nobreak >nul 2>&1
)

"%PY%" "app.py"
pause
