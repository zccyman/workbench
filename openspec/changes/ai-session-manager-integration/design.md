# AI Session Manager Integration — Design

> 版本：1.0.0
> 创建：2026-04-03
> 状态：已实施（补录）

## 1. 架构适配

### 原项目架构
```
ai-session-manager/
├── ai-session-manager/backend/app/
│   ├── main.py          # 独立 FastAPI 入口
│   ├── routes/          # 8 个路由模块
│   ├── services/        # 3 个服务模块
│   ├── models.py
│   ├── database.py
│   └── config.py
```

### Workbench 适配后架构
```
workbench/backend/tools/ai_session_manager/
├── router.py            # 汇总所有子路由，暴露给 discover_tools()
├── config.py            # 数据源路径配置
├── database.py          # SQLite 连接工具
├── models.py            # Pydantic 模型
├── meta.json            # 工具元数据
├── routes/              # 8 个 API 路由模块
│   ├── sessions.py
│   ├── messages.py
│   ├── projects.py
│   ├── search.py
│   ├── stats.py
│   ├── knowledge.py
│   ├── export.py
│   ├── sources.py
│   └── tab_contents.py
└── services/            # 3 个业务服务
    ├── export_service.py
    ├── knowledge_service.py
    └── search_service.py
```

### 关键适配点

| 适配项 | 原项目 | Workbench 适配 |
|--------|--------|----------------|
| 入口 | `app/main.py` 独立启动 | `router.py` 导出 APIRouter，由 `discover_tools()` 注册 |
| 认证 | 无认证 | 复用 Workbench JWT 认证（通过 `Depends(get_current_user)`） |
| 数据库 | 独立 SQLite 连接 | 复用原 config.py 配置，读取外部 Kilo/OpenCode 数据库 |
| 路由前缀 | 直接在 main.py 定义 | 由 `discover_tools()` 自动添加 `/api/tools/ai_session_manager` |
| CORS | 独立配置 | 复用 Workbench 全局 CORS |

## 2. 前端设计

### 页面结构
```
AiSessionManager.tsx
├── 左侧面板（w-80）
│   ├── 搜索框 + 搜索按钮
│   ├── 数据源切换按钮（Kilo Code / OpenCode）
│   └── 会话列表（可滚动）
└── 右侧面板（flex-1）
    ├── 空状态提示
    └── 消息列表（用户/助手对话气泡）
```

### API 调用
- `GET /api/tools/ai_session_manager/sessions` — 获取会话列表
- `GET /api/tools/ai_session_manager/messages/session/{id}/with-parts` — 获取消息详情
- `GET /api/tools/ai_session_manager/search?q=xxx` — 搜索会话

### 状态管理
- 使用 React `useState` 本地状态，不引入全局状态管理
- 数据源切换时自动刷新会话列表

## 3. 测试策略

### 后端测试
- 镜像源码结构：`tests/unit/backend/ai_session_manager/`
- 覆盖所有 8 个路由模块 + 服务模块
- 使用 mock 数据库和 mock 认证

### 前端测试（待补充）
- pathUtils 类测试不适用（AI Session Manager 无路径转换逻辑）
- 需要测试组件渲染和基本交互

## 4. 数据流

```
用户点击会话 → fetchSessionDetail(id) → GET /messages/session/{id}/with-parts
    → 解析 parts JSON → 提取 text 类型内容 → 渲染对话气泡
```

## 5. 已知限制

1. **只读访问**：不修改 Kilo/OpenCode 原始数据库
2. **无浏览器扩展**：TabBitBrowser 相关功能在 Workbench 中不可用
3. **无实时同步**：需要手动刷新获取最新会话
