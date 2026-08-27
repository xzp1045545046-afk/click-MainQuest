#!/bin/bash
# Double-click this file on macOS to start 任务手册 desktop app.
cd "$(dirname "$0")" || exit 1

# 优先使用项目自带虚拟环境；若不存在则回退到系统 python3
if [ -x "./venv/bin/python" ]; then
    PY="./venv/bin/python"
else
    PY="python3"
fi

"$PY" app.py
