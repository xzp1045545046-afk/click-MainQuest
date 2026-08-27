#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务手册本地数据同步服务
- 端口固定 8765，仅监听 127.0.0.1
- GET  /data          读取 data.json（带 CORS，供预览面板跨源拉取）
- POST /data          保存 data.json（带 CORS，处理 OPTIONS 预检）
- 其余路径             静态文件服务（直接打开 http://127.0.0.1:8765/todolist-dnf.html）
"""
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data.json")
PORT = 8765

CTYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".otf": "font/otf",
    ".ttf": "font/ttf",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "TodoSync/1.0"

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def _send_json(self, code, payload, raw=None):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/data":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "rb") as f:
                    payload = f.read()
            else:
                payload = b'{"todos":[]}'
            self._send_json(200, payload)
            return
        if path == "/":
            path = "/todolist-dnf.html"
        fp = os.path.normpath(os.path.join(BASE, path.lstrip("/")))
        if not fp.startswith(BASE + os.sep) or not os.path.isfile(fp):
            self.send_response(404)
            self.end_headers()
            return
        ext = os.path.splitext(fp)[1].lower()
        ctype = CTYPES.get(ext, "application/octet-stream")
        with open(fp, "rb") as f:
            body = f.read()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/data":
            self.send_response(404)
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length)
            obj = json.loads(body.decode("utf-8"))
            if not isinstance(obj, dict) or "todos" not in obj:
                raise ValueError("payload must contain 'todos'")
            tmp = DATA_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)
            os.replace(tmp, DATA_FILE)  # 原子写入，避免写一半损坏
            self._send_json(200, b'{"ok":true}')
        except Exception as exc:  # noqa: BLE001
            self._send_json(400, json.dumps({"ok": False, "err": str(exc)}).encode("utf-8"))

    def log_message(self, fmt, *args):
        sys.stderr.write("[todolist-sync] %s\n" % (fmt % args))


if __name__ == "__main__":
    print("task-manual sync server -> http://127.0.0.1:%d/todolist-dnf.html" % PORT, flush=True)
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
