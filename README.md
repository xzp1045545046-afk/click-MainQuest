# 任务手册（TodoList DNF）

一款像素复古风格的本地任务管理工具，支持 **DNF 暗色主题** 与 **星露谷亮色主题** 切换，可在浏览器、桌面应用和静态托管三种方式下运行。

---

## 项目解决什么问题

日常任务管理工具往往太复杂、太「现代」，或者必须联网注册账号。任务手册希望提供一个：

- **开箱即用**：单 HTML 文件即可运行，无需构建工具。
- **数据本地优先**：任务与头像默认保存在本地 `data.json`，不依赖云端。
- **跨平台可用**：Windows 与 macOS 都有对应的桌面启动脚本。
- **风格鲜明**：像素字体 + 双主题（暗色 DNF / 亮色星露谷），适合喜欢复古游戏风格的用户。

---

## 主要功能

### 任务管理

- 添加任务：支持任务标题、详情备注、选择「主线」或「支线」。
- 任务列表：按「进行中 / 主线 / 支线 / 已完成」筛选查看。
- 完成任务：点击任务项上的圆圈标记完成，任务会自动进入「已完成」视图。
- 拖拽排序：在「进行中」列表里按住任务项可上下拖拽调整顺序。
- 编辑 / 删除：选中任务后右侧抽屉面板支持修改或删除。

### 数据与持久化

- **桌面版**：通过 `app.py` 启动，数据自动写入 `data.json`，关闭窗口 / 重启电脑不丢失。
- **本地浏览器版**：通过 `server.py` 启动（端口 8765），数据同时写入 `data.json` 和浏览器 localStorage。
- **线上版**：托管为静态页面后，数据仅保存在浏览器 localStorage 中。

### 头像

- 左侧头像区域未上传时显示「上传头像」引导。
- 已上传时显示图片，鼠标悬停显示遮罩层和「更换头像」提示。
- 头像数据随任务数据一起保存到 `data.json`（桌面版）或 localStorage（线上版）。

### 导出 / 导入

- 左侧 rail 提供「导出」「导入」按钮。
- 桌面版调用系统文件对话框，线上版使用浏览器下载 / 上传 JSON 文件。
- 用于备份、迁移或在不同设备间恢复任务数据。

### 主题切换

- 默认 DNF 暗色主题。
- 左下角主题切换按钮可切换到星露谷亮色主题。
- 主题偏好自动保存在 localStorage。

---

## 安装方法

### 1. 克隆或下载项目

```bash
git clone <你的仓库地址>
cd todolist-dnf
```

### 2. 安装依赖

本项目依赖很少：

- **浏览器版**：任意现代浏览器，零依赖。
- **本地同步服务**：Python 3.8+。
- **桌面版**：Python 3.8+ 和 pywebview。

安装 pywebview（推荐使用虚拟环境）：

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
pip install pywebview
```

> Windows 用户还需要安装 [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)，通常现代 Windows 10/11 已自带。

---

## 使用方法

### 方式一：桌面应用（推荐 Windows / macOS）

#### Windows

双击 `run.bat`：

```bash
run.bat
```

调试时可用 `run_debug.bat`，保留黑色控制台窗口查看错误。

#### macOS

双击 `run.command`：

```bash
./run.command
```

如果提示没有执行权限，先在终端运行：

```bash
chmod +x run.command
```

#### 手动启动

```bash
python3 app.py
```

### 方式二：本地浏览器版

```bash
python3 server.py
```

然后打开浏览器访问：

```
http://127.0.0.1:8765/todolist-dnf.html
```

### 方式三：静态托管（线上版）

将 `todolist-dnf.html` 和 `fonts/` 目录一起部署到任意静态托管服务即可。`dist/` 目录就是已经准备好的线上部署产物。

---

## 输入输出示例

### 任务数据格式（`data.json`）

```json
{
  "todos": [
    {
      "id": "1718880000000-0",
      "text": "完成 README",
      "detail": "补充安装与使用说明",
      "major": "主线",
      "done": true,
      "completedAt": "2026-08-27T10:00:00",
      "order": 0
    },
    {
      "id": "1718883600000-1",
      "text": "购买咖啡豆",
      "detail": "深烘，500g",
      "major": "支线",
      "done": false,
      "completedAt": null,
      "order": 1
    }
  ],
  "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 时间戳 + 序号生成的唯一标识 |
| `text` | string | 任务标题 |
| `detail` | string | 任务详情 / 备注 |
| `major` | string | `主线` 或 `支线` |
| `done` | boolean | 是否完成 |
| `completedAt` | string \| null | 完成时间 ISO 字符串 |
| `order` | number | 同类型任务内的排序权重 |
| `avatar` | string \| null | 头像图片的 base64 data URL |

### 导出 / 导入示例

点击左侧「导出」按钮，会生成如下内容的 JSON 备份文件：

```json
{
  "todos": [ ... ],
  "avatar": null
}
```

点击「导入」按钮选择上述 JSON 文件，即可覆盖恢复当前任务数据。

---

## 项目结构

```
todolist-dnf/
├── todolist-dnf.html          # 主程序（单文件 HTML/CSS/JS）
├── app.py                     # 桌面版入口（pywebview）
├── server.py                  # 本地浏览器同步服务
├── run.bat                    # Windows 启动脚本
├── run_debug.bat              # Windows 调试启动脚本
├── run.command                # macOS 启动脚本
├── fonts/                     # 像素字体资源
├── icons/                     # 图标资源
├── data.json                  # 本地任务数据（自动生成，git 忽略）
├── dist/                      # 线上部署产物（git 忽略）
└── 任务手册-完整规格.md        # 详细复刻规格
```

---

## 许可证

本项目使用 [MIT License](LICENSE)。
