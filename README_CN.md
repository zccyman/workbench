# Workbench

[English](README.md)

个人工具箱网站 — 集成各种日常工具的 Web 应用。

## 功能特点

- 🔧 **自动发现**：创建目录即可添加新工具，零配置
- 🔒 **用户认证**：登录保护的个人工具箱
- 🌙 **主题切换**：亮色/暗色模式
- 📱 **响应式**：适配桌面和移动端

## 技术栈

- **后端**：Python + FastAPI + SQLite
- **前端**：React + TypeScript + Vite + Tailwind CSS

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.8+

### 安装

```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### 启动

```bash
./start.sh
```

或手动启动：

```bash
# 后端（端口 8001）
cd backend && uvicorn main:app --host 0.0.0.0 --port 8001

# 前端（端口 5173）
cd frontend && npm run dev
```

## 添加新工具

1. 创建 `backend/tools/<tool_id>/` 目录
2. 添加 `router.py`，包含 FastAPI `APIRouter`
3. 添加 `meta.json` 工具元数据
4. 创建前端页面 `frontend/src/pages/tools/<ToolName>.tsx`
5. 重启服务 — 工具自动注册！

### meta.json 示例

```json
{
  "name": "My Tool",
  "id": "my_tool",
  "description": "工具描述",
  "icon": "🛠️",
  "category": "开发工具",
  "version": "1.0.0"
}
```

## 已包含工具

| 工具 | 描述 |
|------|------|
| WSL Path Bridge | 浏览 WSL 文件系统，WSL 与 Windows 路径格式互转 |
| AI Session Manager | 管理 Kilo Code 和 OpenCode 的 AI 编码会话 — 搜索、浏览消息、导出和统计 |
| AI Session Manager | 管理 Kilo Code 和 OpenCode 的 AI 编码会话 — 搜索、浏览消息、导出和统计 |

## 许可证

[MIT](LICENSE)
