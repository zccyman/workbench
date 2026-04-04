# Agent Monitor — Tasks

> 版本：1.0.0 | 创建：2026-04-04 | 状态：Draft

## Task 列表

### Task 1: 后端骨架

创建 `backend/tools/agent_monitor/` 目录结构，编写 `meta.json`、`models.py`（Pydantic 响应模型）、`router.py`（骨架 + 健康检查端点）。

**验证**：重启后端后 `GET /api/tools` 返回 agent_monitor，`GET /api/tools/agent-monitor/health` 返回 200。

🏷️ Ship

---

### Task 2: 采集层 collector.py

实现 `collector.py`，复用 `ai_session_manager` 的 database/config 和 `usage_monitor` 的 collector，组合出统一的数据采集接口 `collect_all_data()`。

**验证**：能正确返回 KiloCode 和 OpenCode 的会话列表，包含 session_id、project_name、agent_type、model、message_count。

🏷️ Show

---

### Task 3: 分析层 analyzer.py

实现 `analyzer.py`，包含：
- `estimate_tokens(message_count, model)` — 基于消息数和模型估算 token
- `estimate_cost(tokens, model)` — 基于 token 和模型单价估算成本
- `aggregate_trend(sessions, period)` — 按日/周/月聚合趋势数据
- `compute_model_breakdown(sessions)` — 模型使用分布
- `detect_agent_status(sessions)` — Agent 状态检测

**验证**：单元测试覆盖所有函数，给定 mock 数据输出正确的 token/成本/趋势。

🏷️ Show

---

### Task 4: 后端 API 完整实现

实现全部 8 个 API 端点：
- `GET /overview` — 总览数据
- `GET /sessions` — 会话列表（分页+过滤）
- `GET /sessions/{id}` — 会话详情
- `GET /agents` — Agent 状态列表
- `GET /token-trend` — Token 趋势
- `GET /cost-trend` — 成本趋势
- `GET /model-breakdown` — 模型分布
- `GET /health` — 健康检查（Task 1 已实现骨架）

**验证**：每个端点返回正确格式的 JSON，分页/过滤参数生效。

🏷️ Show

---

### Task 5: 前端骨架 + DashboardOverview

创建 `AgentMonitor.tsx` 主页面（Tab 布局骨架）和 `DashboardOverview.tsx` 概览组件（4 个统计卡片：活跃 Agent、今日会话、Token、成本）。

**验证**：页面可正常渲染，调用 `/api/tools/agent-monitor/overview` 显示数据。

🏷️ Show

---

### Task 6: 图表组件

实现 3 个 recharts 图表组件：
- `TokenChart.tsx` — AreaChart，Token 消耗趋势（按 Agent 分色）
- `CostChart.tsx` — BarChart，成本趋势（按 Agent 分色）
- `ModelPieChart.tsx` — PieChart，模型使用分布

**验证**：每个组件接收 mock 数据能正确渲染图表，坐标轴/图例/tooltip 正常。

🏷️ Show

---

### Task 7: 状态组件

实现 2 个状态组件：
- `AgentStatusCard.tsx` — Agent 状态卡片（运行中/空闲/离线，带颜色标识）
- `SessionTimeline.tsx` — 会话时间线列表（显示模型、时长、估算成本）

**验证**：组件正确渲染，Agent 状态颜色正确（🟢运行/🟡空闲/⚪离线），会话列表支持滚动。

🏷️ Show

---

### Task 8: 联调测试

前后端联调，确保所有组件数据流正确。编写后端单元测试。

**验证**：
- 后端：`pytest tests/unit/backend/agent_monitor/ -v` 全部通过
- 前端：页面正常加载所有组件，无控制台错误
- 数据：各图表显示真实数据而非 mock

🏷️ Show

---

### Task 9: 文档收尾

更新 README.md/README_CN.md 工具列表，更新 `.dev-workflow.md` 记录决策，更新 `openspec/design.md` 添加 Agent Monitor 章节。

**验证**：README 中 Agent Monitor 描述准确，.dev-workflow.md 有新决策记录。

🏷️ Ship
