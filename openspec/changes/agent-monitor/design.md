# Agent Monitor — Design

> 版本：1.0.0 | 创建：2026-04-04 | 状态：Draft

## 1. 架构概述

```
┌──────────────────────────────────────────────────────────┐
│                    Agent Monitor                         │
├──────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript + recharts)                │
│  ┌─────────────────┬──────────────────────────────────┐  │
│  │ DashboardOverview│  TokenChart / CostChart / Pie    │  │
│  │ AgentStatusCard │  SessionTimeline                  │  │
│  └─────────────────┴──────────────────────────────────┘  │
│                          ↕ HTTP                          │
│  Backend (FastAPI)                                       │
│  ┌────────────┬──────────────┬───────────────────────┐   │
│  │ router.py  │ collector.py │  analyzer.py          │   │
│  │ (8 端点)   │ (数据采集)    │  (token/成本/趋势)     │   │
│  └────────────┴──────────────┴───────────────────────┘   │
│       ↕                    ↕                             │
│  ┌─────────────────────┬────────────────────────────┐    │
│  │ ai_session_manager  │ usage_monitor              │    │
│  │ (database/config)   │ (collector)                │    │
│  └─────────────────────┴────────────────────────────┘    │
│       ↕                                                  │
│  workbench.db + KiloCode/OpenCode SQLite sessions.db     │
└──────────────────────────────────────────────────────────┘
```

## 2. 最终目录结构

```
workbench/
├── backend/tools/agent_monitor/
│   ├── __init__.py
│   ├── meta.json
│   ├── models.py              # Pydantic 响应模型
│   ├── router.py              # FastAPI 路由
│   ├── collector.py           # 数据采集（复用现有服务）
│   └── analyzer.py            # 数据分析（token/成本/趋势）
├── frontend/src/pages/tools/AgentMonitor.tsx
├── frontend/src/components/agent_monitor/
│   ├── DashboardOverview.tsx
│   ├── SessionTimeline.tsx
│   ├── TokenChart.tsx
│   ├── CostChart.tsx
│   ├── ModelPieChart.tsx
│   └── AgentStatusCard.tsx
├── tests/unit/backend/agent_monitor/
│   ├── test_collector.py
│   ├── test_analyzer.py
│   └── test_router.py
```

## 3. Import 路径映射

| 文件 | 需要 Import 的路径 |
|------|-------------------|
| `collector.py` | `from backend.tools.ai_session_manager.database import get_db`<br>`from backend.tools.ai_session_manager.models import Session, SessionWithProject`<br>`from backend.tools.ai_session_manager.config import get_project_dirs`<br>`from backend.tools.usage_monitor.collector import collect_events` |
| `analyzer.py` | `from backend.tools.agent_monitor.collector import collect_all_data`<br>`from backend.tools.agent_monitor.models import *` |
| `router.py` | `from backend.tools.agent_monitor.collector import collect_all_data`<br>`from backend.tools.agent_monitor.analyzer import *`<br>`from backend.tools.agent_monitor.models import *` |

## 4. API 设计

### 4.1 总览数据

```
GET /api/tools/agent-monitor/overview
```

**响应**：
```json
{
  "active_agents": 3,
  "total_sessions_today": 12,
  "total_sessions_week": 45,
  "estimated_tokens_today": 45000,
  "estimated_cost_today": 0.42,
  "most_used_model": "claude-sonnet-4-20250514"
}
```

### 4.2 会话列表

```
GET /api/tools/agent-monitor/sessions?limit=50&offset=0&agent=kilocode&date_from=2026-04-01
```

**响应**：
```json
{
  "sessions": [
    {
      "session_id": "abc123",
      "project_name": "workbench",
      "agent_type": "kilocode",
      "model": "minimax-m2.5",
      "start_time": "2026-04-04T10:00:00",
      "end_time": "2026-04-04T10:30:00",
      "message_count": 25,
      "estimated_tokens": 12000,
      "estimated_cost": 0.00
    }
  ],
  "total": 120
}
```

### 4.3 会话详情

```
GET /api/tools/agent-monitor/sessions/{session_id}
```

### 4.4 Agent 列表及状态

```
GET /api/tools/agent-monitor/agents
```

**响应**：
```json
{
  "agents": [
    {
      "name": "KiloCode",
      "type": "kilocode",
      "status": "running",
      "active_sessions": 2,
      "last_active": "2026-04-04T10:30:00",
      "model": "minimax-m2.5"
    },
    {
      "name": "OpenCode",
      "type": "opencode",
      "status": "idle",
      "active_sessions": 0,
      "last_active": "2026-04-04T09:15:00",
      "model": "glm-4.7"
    }
  ]
}
```

### 4.5 Token 趋势

```
GET /api/tools/agent-monitor/token-trend?period=week
```

**响应**：
```json
{
  "data": [
    {"date": "2026-04-01", "kilocode": 15000, "opencode": 8000},
    {"date": "2026-04-02", "kilocode": 22000, "opencode": 12000},
    {"date": "2026-04-03", "kilocode": 18000, "opencode": 5000}
  ]
}
```

### 4.6 成本趋势

```
GET /api/tools/agent-monitor/cost-trend?period=week
```

**响应**：
```json
{
  "data": [
    {"date": "2026-04-01", "kilocode": 0.00, "opencode": 0.15},
    {"date": "2026-04-02", "kilocode": 0.00, "opencode": 0.28},
    {"date": "2026-04-03", "kilocode": 0.00, "opencode": 0.12}
  ]
}
```

### 4.7 模型分布

```
GET /api/tools/agent-monitor/model-breakdown?period=week
```

**响应**：
```json
{
  "models": [
    {"name": "claude-sonnet-4-20250514", "count": 45, "percentage": 37.5},
    {"name": "glm-4.7", "count": 35, "percentage": 29.2},
    {"name": "minimax-m2.5", "count": 40, "percentage": 33.3}
  ]
}
```

### 4.8 健康检查

```
GET /api/tools/agent-monitor/health
```

**响应**：
```json
{
  "status": "healthy",
  "sources": {
    "ai_session_manager": "connected",
    "usage_monitor": "connected",
    "database": "connected"
  }
}
```

## 5. 模型单价配置

```python
MODEL_PRICES = {
    # per million tokens ($/MTok)
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-5-20251022": {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "glm-4.7": {"input": 1.00, "output": 5.00},
    "glm-4.6": {"input": 1.00, "output": 5.00},
    "minimax-m2.5": {"input": 0.00, "output": 0.00},  # free
    "gpt-5.3-codex": {"input": 2.50, "output": 12.50},
    "gemini-2.5-pro": {"input": 2.50, "output": 10.00},
}
```

**Token 估算公式**：
- 每条消息平均 500 tokens（input + output 合计）
- `estimated_tokens = message_count * 500`
- `estimated_cost = (estimated_tokens / 1_000_000) * avg_price`
- 免费模型（minimax-m2.5）成本为 0

## 6. Agent 状态检测

| 状态 | 判定条件 |
|------|----------|
| `running` | 进程存在 + 最近 5 分钟内有新会话活动 |
| `idle` | 进程存在 + 最近 5 分钟内无新会话活动 |
| `offline` | 进程不存在 |

**进程检测方式**：
- KiloCode：`ps aux | grep -i kilo` 或检查 `.kilocode/` 下活跃 session 文件修改时间
- OpenCode：`ps aux | grep -i opencode` 或检查 `.opencode/` 下活跃 session 文件修改时间

## 7. 前端页面布局

```
┌─────────────────────────────────────────────────────┐
│  Agent Monitor                              🔄 刷新  │
├─────────────────────────────────────────────────────┤
│ [🟢 3 Agent] [📋 12 会话] [📊 45K Token] [💰 $0.42]│
├──────────────┬──────────────────────────────────────┤
│ Agent 状态    │ Token 趋势 (AreaChart)               │
│ ┌──────────┐ │                                      │
│ │ KiloCode │ ├──────────────────────────────────────┤
│ │ OpenCode │ │ 成本趋势 (BarChart)                  │
│ └──────────┘ │                                      │
│              ├──────────────────────────────────────┤
│ 模型分布      │ 会话时间线 (列表)                     │
│ (PieChart)   │                                      │
└──────────────┴──────────────────────────────────────┘
```

## 8. 风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| KiloCode/OpenCode 数据格式变更 | 解析失败 | 复用 ai_session_manager 的解析逻辑，它已适配 |
| Token 估算不准确 | 成本显示偏差 | 首期用估算，后续可接入精确 API |
| 轮询性能开销 | 频繁查询数据库 | 5 秒间隔 + 缓存，影响可控 |
| 与现有工具耦合 | ai_session_manager 变更影响监控 | 接口稳定，变更概率低 |
