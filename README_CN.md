# Workbench

个人工具箱网站 — 日常工具集合，随时取用。

## 特性

- 🔧 **自动发现**：新建目录即可添加工具，零配置
- 🔒 **认证系统**：登录保护，个人私密工具箱
- 🌙 **主题切换**：明暗模式
- 📱 **响应式**：支持桌面和移动端

## 技术栈

- **后端**：Python + FastAPI + SQLite
- **前端**：React + TypeScript + Vite + Tailwind CSS

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.8+

### 安装

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 运行

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

## 添加新工具

1. 创建 `backend/tools/<tool_id>/` 目录
2. 添加 `router.py`，包含一个 FastAPI `APIRouter`
3. 添加 `meta.json`，包含工具元数据
4. 创建前端页面 `frontend/src/pages/tools/<ToolName>.tsx`
5. 重启服务 — 工具自动注册！

### meta.json 示例

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

## 已包含工具

| 工具 | 描述 |
|------|------|
| WSL Path Bridge | 浏览WSL文件系统，转换WSL和Windows路径格式 |

## 许可证

MIT
