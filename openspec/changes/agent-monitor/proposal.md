# Agent Monitor — Proposal

> 版本：1.0.0 | 创建：2026-04-04 | 状态：Draft

## 做什么

自研一个轻量 AI Agent 监控层（Agent Monitor），以 FastAPI 工具形式入驻 workbench，作为 `backend/tools/agent_monitor/`，配套前端可视化页面。同时监控 **KiloCode** 和 **OpenCode** 的 Agent 运行状态、Token 消耗和成本。

## 为什么

1. **实时监控需求** — 需要同时监控 KiloCode 和 OpenCode 的 Agent 运行状态，现有工具（AI Session Manager 侧重历史浏览，Usage Monitor 侧重 OpenClaw 工具分析）不覆盖此场景
2. **Token/成本追踪** — 按会话/模型/时间维度追踪 token 消耗和估算成本，防止 runaway loop 产生意外费用
3. **统一监控视图** — 在 workbench 中提供一站式 Agent 监控面板，无需切换多个终端或工具

## 数据来源

| 数据 | 来源 | 复用方式 |
|------|------|----------|
| 会话列表/详情 | AI Session Manager database | 直接调用 `ai_session_manager.database.get_db()` 和 models |
| 项目目录列表 | AI Session Manager config | 调用 `ai_session_manager.config.get_project_dirs()` |
| 工具调用/技能读取 | Usage Monitor collector | 调用 `usage_monitor.collector.collect_events()` |
| Token/成本估算 | 自研分析层 | 基于会话消息数 × 模型单价估算 |
| Agent 状态 | 进程检测 + 会话活跃度 | 自研（检测 kilo/opencode 进程 + 最近活跃时间） |

## 暂不实现

| 功能 | 原因 |
|------|------|
| WebSocket 实时推送 | 首期用轮询（5秒），降低复杂度 |
| 多用户隔离 | 个人工具，单用户即可 |
| 告警通知 | 后续迭代 |
| 精确 Token 计数 | KiloCode/OpenCode 不暴露精确 token 数，首期用消息数 × 模型平均估算 |

## 功能清单

| # | 功能 | 说明 |
|---|------|------|
| 1 | Agent 状态面板 | 检测 KiloCode/OpenCode 进程，显示运行中/空闲/离线 |
| 2 | 会话总览 | 今日/本周/本月会话数、活跃 Agent 数 |
| 3 | Token 趋势 | 按日/周/月展示 token 消耗趋势（AreaChart） |
| 4 | 成本趋势 | 按日/周/月展示成本趋势（BarChart） |
| 5 | 模型分布 | 各模型调用占比（PieChart） |
| 6 | 会话时间线 | 按时间排序的会话列表，显示模型、时长、估算成本 |
| 7 | 健康检查 | 数据源连通性验证 |

## 目录结构草案

```
backend/tools/agent_monitor/
├── __init__.py
├── meta.json
├── router.py              # FastAPI APIRouter（8 个端点）
├── models.py              # Pydantic 请求/响应模型
├── collector.py           # 数据采集：复用 ai_session_manager + usage_monitor
└── analyzer.py            # 数据分析：token 估算、成本计算、趋势聚合

frontend/src/pages/tools/AgentMonitor.tsx              # 主页面（Tab 布局）
frontend/src/components/agent_monitor/
├── DashboardOverview.tsx   # 顶部概览卡片
├── SessionTimeline.tsx     # 实时会话时间线
├── TokenChart.tsx          # Token 消耗趋势（AreaChart）
├── CostChart.tsx           # 成本趋势（BarChart）
├── ModelPieChart.tsx       # 模型使用分布（PieChart）
└── AgentStatusCard.tsx     # Agent 状态卡片

tests/unit/backend/agent_monitor/
├── test_collector.py
├── test_analyzer.py
└── test_router.py
```

## 原始项目保护

本项目为自研，不修改任何外部项目。数据来源为 workbench 内部已有工具。
