# 🛠️ Workbench

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## A personal toolbox website — a collection of daily-use tools in one place.

### Features

- 🔧 **Auto-discovery**: Add a new tool by creating a directory — no config needed
- 🔒 **Authentication**: Login-protected personal tools
- 🌙 **Theme Support**: Light and dark modes
- 📱 **Responsive**: Works on desktop and mobile

### Tech Stack

- **Backend**: Python + FastAPI + SQLite
- **Frontend**: React + TypeScript + Vite + Tailwind CSS

### Getting Started

#### Prerequisites

- Node.js 18+
- Python 3.8+

#### Installation

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

#### Run

```bash
./start.sh
```

Or manually:

```bash
# Backend (port 8001)
cd backend && uvicorn main:app --reload --port 8001

# Frontend (port 5173)
cd frontend && npm run dev
```

### Adding a New Tool

1. Create `backend/tools/<tool_id>/` directory
2. Add `router.py` with a FastAPI `APIRouter`
3. Add `meta.json` with tool metadata
4. Create frontend page `frontend/src/pages/tools/<ToolName>.tsx`
5. Restart the server — tool auto-registers!

#### meta.json Example

```json
{
  "name": "My Tool",
  "id": "my_tool",
  "description": "A description of my tool",
  "icon": "🛠️",
  "category": "开发工具",
  "version": "1.0.0"
}
```

### Included Tools

| Tool | Description |
|------|-------------|
| WSL Path Bridge | Browse WSL filesystem and convert paths between WSL and Windows formats |

---

<a id="中文"></a>

## 个人工具箱网站 — 集成各种日常工具的 Web 应用

### 功能特点

- 🔧 **自动发现**：创建目录即可添加新工具，零配置
- 🔒 **用户认证**：登录保护的个人工具箱
- 🌙 **主题切换**：亮色/暗色模式
- 📱 **响应式**：适配桌面和移动端

### 技术栈

- **后端**：Python + FastAPI + SQLite
- **前端**：React + TypeScript + Vite + Tailwind CSS

### 快速开始

#### 环境要求

- Node.js 18+
- Python 3.8+

#### 安装

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

#### 启动

```bash
./start.sh
```

或手动启动：

```bash
# 后端（端口 8001）
cd backend && uvicorn main:app --reload --port 8001

# 前端（端口 5173）
cd frontend && npm run dev
```

### 添加新工具

1. 创建 `backend/tools/<tool_id>/` 目录
2. 添加 `router.py`，包含一个 FastAPI `APIRouter`
3. 添加 `meta.json` 工具元数据
4. 创建前端页面 `frontend/src/pages/tools/<ToolName>.tsx`
5. 重启服务器 — 工具自动注册！

#### meta.json 示例

```json
{
  "name": "我的工具",
  "id": "my_tool",
  "description": "工具描述",
  "icon": "🛠️",
  "category": "开发工具",
  "version": "1.0.0"
}
```

### 已包含工具

| 工具 | 描述 |
|------|------|
| WSL 路径转换 | 浏览 WSL 文件系统，WSL 与 Windows 路径格式互转 |

---

## License

[MIT](LICENSE)
