# AI Session Manager Integration — Proposal

> 变更类型：Feature Addition
> 状态：已实施（补录）
> 日期：2026-04-03

## 做什么

将 AI Session Manager 作为第二个工具入驻 Workbench 工具箱网站，使用户可以在 Workbench 中统一管理 Kilo Code 和 OpenCode 的会话数据。

## 为什么

- AI Session Manager 是独立开发的工具，需要集成到 Workbench 的统一入口中
- 用户已在 Workbench 中登录，无需额外认证即可使用会话管理功能
- 验证 Workbench 工具自动发现机制对复杂工具（多路由、多服务）的支持能力

## 范围

### 包含
- 后端：将 AI Session Manager 代码适配到 `backend/tools/ai_session_manager/` 目录
- 前端：创建 `AiSessionManager.tsx` 页面并注册到 App.tsx 路由
- 测试：补充后端单元测试（已完成 100 个测试）
- 配置：创建 `meta.json` 工具元数据

### 不包含
- 浏览器扩展（TabBitBrowser extension）— 不在 Workbench 范围内
- Docker 部署 — Workbench 优先本地运行
- 独立后端服务 — 复用 Workbench 的 FastAPI app 和认证机制

## 影响

- 后端新增约 2000 行代码（routes + services + models）
- 前端新增约 140 行代码
- 测试新增 100 个后端单元测试
- 不影响已有 WSL Path Bridge 工具
