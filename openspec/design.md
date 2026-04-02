# Workbench - 个人工具箱网站 Design Spec

> 版本：1.0.0
> 创建：2026-04-02
> 状态：Draft

---

## 1. 项目概述

**Workbench** 是一个开源的个人工具箱网站，集合日常频繁使用的各类小工具，随时取用。

## 2. 核心决策

| 决策项 | 选择 |
|--------|------|
| 开源/闭源 | 开源（MIT） |
| 认证 | 需要登录 |
| 部署 | 优先本地，支持扩展部署 |
| 工具注册 | 自动发现（扫描 tools/ 目录 + meta.json） |
| 数据库 | SQLite（本地优先） |

## 3. 技术栈

- **后端**：Python 3.8+ / FastAPI / SQLite / JWT 认证
- **前端**：React 18+ / TypeScript / Vite / Tailwind CSS
- **启动**：start.sh 一键启动前后端

## 4. 目录结构

```
workbench/
├── backend/
│   ├── main.py                 # FastAPI 入口，自动扫描注册工具
│   ├── database.py             # SQLite 数据库
│   ├── auth/                   # JWT 认证模块
│   │   ├── router.py
│   │   ├── models.py
│   │   └── deps.py
│   ├── tools/                  # 工具目录（自动发现）
│   │   ├── __init__.py
│   │   └── wsl_path_bridge/
│   │       ├── __init__.py
│   │       ├── router.py       # 工具 API 路由
│   │       ├── storage.py
│   │       └── meta.json       # 工具元数据
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── wsl/            # WSL工具组件
│   │   ├── pages/
│   │   │   ├── Home.tsx        # 工具列表首页
│   │   │   ├── Login.tsx
│   │   │   └── tools/
│   │   │       └── WslPathBridge.tsx
│   │   ├── utils/
│   │   │   ├── api.ts
│   │   │   └── pathUtils.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── tsconfig.json
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── backend/
│   │   │   └── test_tool_discovery.py
│   │   └── frontend/
│   └── integration/
│       └── test_api.py
├── docs/
├── openspec/
│   └── design.md
├── start.sh
├── .gitignore
├── README.md
└── README_CN.md
```

## 5. 工具自动发现机制

### 5.1 后端

`main.py` 启动时：
1. 扫描 `backend/tools/` 下所有子目录
2. 检查是否存在 `router.py` 和 `meta.json`
3. 读取 `meta.json` 获取工具元数据
4. 将 `router.py` 中的 APIRouter 自动注册到 app
5. 生成工具列表 API：`GET /api/tools`

### 5.2 meta.json 约定

```json
{
  "name": "WSL Path Bridge",
  "id": "wsl_path_bridge",
  "description": "WSL路径转换工具",
  "icon": "🔄",
  "category": "开发工具",
  "version": "1.0.0"
}
```

### 5.3 前端

1. 首页调用 `GET /api/tools` 获取工具列表
2. 根据工具 id 动态加载 `pages/tools/<ToolName>.tsx` 组件
3. 每个工具页面自行负责其 UI 和 API 调用

### 5.4 添加新工具流程

```
1. 创建 backend/tools/<tool_id>/ 目录
2. 编写 router.py（FastAPI APIRouter）
3. 编写 meta.json（工具元数据）
4. 创建前端页面 pages/tools/<ToolName>.tsx
5. 重启服务 → 自动生效
```

## 6. API 设计

### 认证
- `POST /api/auth/login` — 登录
- `POST /api/auth/register` — 注册
- `GET /api/auth/me` — 当前用户信息

### 工具
- `GET /api/tools` — 工具列表（自动发现）

### WSL Path Bridge
- `GET /api/tools/wsl-path-bridge/browse` — 浏览文件
- `POST /api/tools/wsl-path-bridge/convert` — 转换路径
- `GET /api/tools/wsl-path-bridge/favorites` — 获取收藏
- `POST /api/tools/wsl-path-bridge/favorites` — 添加收藏
- `DELETE /api/tools/wsl-path-bridge/favorites/{id}` — 删除收藏

## 7. 开发任务清单

### Phase 1：框架重构
- [x] T1: 后端工具自动发现机制（扫描 + 注册 + 工具列表API） — `main.py:discover_tools()` ✅
- [x] T2: wsl_path_bridge 添加 meta.json — `backend/tools/wsl_path_bridge/meta.json` ✅
- [x] T3: 后端 main.py 重构（集成自动发现） — `main.py` 已集成 ✅
- [x] T4: 前端首页重构（动态工具列表） — `Home.tsx` 调用 `/api/tools` ✅
- [x] T5: 前端路由重构（动态工具路由） — `App.tsx` 注册工具路由 ✅

### Phase 2：基础设施
- [x] T6: 添加 .gitignore — 已存在（待补充完善）
- [x] T7: 添加 README.md + README_CN.md — 双语 README 已完成 ✅
- [x] T8: 添加 tests/ 基础结构 + conftest.py — `tests/conftest.py` ✅
- [x] T9: 工具发现机制单元测试 — `tests/unit/backend/test_tool_discovery.py` ✅

### Phase 3：WSL Path Bridge 适配
- [x] T10: 确认 wsl_path_bridge 适配新框架 — `router.py` + `storage.py` + `meta.json` ✅
- [x] T11: WSL 工具前端适配 — `WslPathBridge.tsx` + 6 个组件 ✅

### Phase 4：补充完善
- [x] T12: 补充 wsl_path_bridge 后端 API 单元测试 — `tests/unit/backend/wsl_path_bridge/` (11 tests) ✅
- [x] T13: 补充 wsl_path_bridge 前端 pathUtils 单元测试 — `frontend/src/utils/__tests__/pathUtils.test.ts` (25 tests) ✅
- [x] T14: 实现主题 API（GET/POST /api/theme） — `main.py:get_theme/update_theme` ✅
- [x] T15: 创建 .kilocode/ 目录 + kilo.json ✅
- [x] T16: 完善 .gitignore ✅
- [x] T17: 创建 .dev-workflow.md 上下文文件 ✅

---

*生成时间：2026-04-02*
*最后更新：2026-04-03*
