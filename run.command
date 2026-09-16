#!/bin/bash
# Double-click this file on macOS to start 任务手册 desktop app.
cd "$(dirname "$0")" || exit 1

# 优先使用项目自带虚拟环境；若不存在则回退到系统 python3
if [ -x "./venv/bin/python" ]; then
    PY="./venv/bin/python"
else
    PY="python3"
fi

# 确保本地同步服务（8765）在线，桌面版需经 http origin 加载才能用云同步
if ! lsof -i :8765 -sTCP:LISTEN >/dev/null 2>&1; then
    "$PY" server.py >/dev/null 2>&1 &
    sleep 2
fi

"$PY" app.py
