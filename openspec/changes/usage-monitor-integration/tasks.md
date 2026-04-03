# Usage Monitor Integration — Tasks

> 版本：1.0.0 | 创建：2026-04-04

## 任务拆分

### Task 1: 后端骨架搭建
- 创建 `backend/tools/usage_monitor/` 目录
- 创建 `__init__.py`
- 创建 `meta.json`（工具元数据）
- 创建空的 `models.py`, `collector.py`, `analyzer.py`, `reporter.py`, `router.py`
- 验证：重启后端，日志显示 "✅ 注册工具: Usage Monitor (usage_monitor)"

**Ship/Show/Ask**: 🚢 Ship（纯骨架，不影响现有功能）

---

### Task 2: Pydantic Models
- 在 `models.py` 中定义所有请求/响应模型（见 design.md §2.3）
- 验证：`python -c "from tools.usage_monitor.models import AnalysisRequest"` 无报错

**Ship/Show/Ask**: 🚢 Ship

---

### Task 3: Collector（JSONL 解析器）
- 重写 `collector.ts` → `collector.py`
- 核心函数：`collect_events(agent_dir, from_date, to_date) → (tool_calls, skill_reads, sessions)`
- 支持：扫描 `.jsonl` 文件、提取 toolCall 事件、检测 SKILL.md 读取
- 容错：跳过无法解析的行和文件
- 验证：编写 `tests/unit/backend/usage_monitor/test_collector.py`（使用 fixture JSONL 文件）

**Ship/Show/Ask**: 👀 Show（核心逻辑，需验证）

---

### Task 4: Analyzer（数据分析器）
- 重写 `analyzer.ts` → `analyzer.py`
- 核心函数：`analyze(tool_calls, skill_reads, sessions, period) → AnalysisResult`
- 输出：工具频率、技能频率、24小时分布、每日活跃度
- 验证：编写 `tests/unit/backend/usage_monitor/test_analyzer.py`

**Ship/Show/Ask**: 👀 Show（核心逻辑，需验证）

---

### Task 5: Reporter（报告格式化）
- 重写 `reporter.ts` → `reporter.py`
- 函数：`format_markdown(result) → str`, `format_json(result) → str`
- 验证：单元测试

**Ship/Show/Ask**: 🚢 Ship

---

### Task 6: Router（API 路由）
- 编写 `router.py`，注册以下端点：
  - `GET /analyze` — 查询参数分析
  - `POST /analyze` — 请求体分析
  - `GET /report/markdown` — Markdown 报告
- 验证：`tests/unit/backend/usage_monitor/test_router.py`

**Ship/Show/Ask**: 👀 Show（API 接口，需验证）

---

### Task 7: 后端集成测试
- 运行所有 usage_monitor 相关测试
- 验证：`pytest tests/unit/backend/usage_monitor/ -v` 全部通过

**Ship/Show/Ask**: 👀 Show

---

### Task 8: 前端骨架 + ConfigPanel
- 创建 `frontend/src/pages/tools/UsageMonitor.tsx`
- 创建 `frontend/src/components/usage_monitor/ConfigPanel.tsx`
- ConfigPanel 包含：Agent 选择、时间过滤、分析按钮
- 在 `App.tsx` 中注册路由 `tools/usage_monitor`
- 验证：前端能编译，页面能渲染

**Ship/Show/Ask**: 👀 Show

---

### Task 9: 前端图表组件
- 创建 `SummaryCards.tsx` — 汇总卡片
- 创建 `ToolFrequencyChart.tsx` — 工具使用柱状图
- 创建 `SkillFrequencyChart.tsx` — 技能激活柱状图
- 创建 `HourlyHeatmap.tsx` — 24小时分布
- 创建 `DailyActivityChart.tsx` — 每日活跃度折线图
- 全部使用 recharts
- 验证：`tsc --noEmit` 无类型错误

**Ship/Show/Ask**: 👀 Show

---

### Task 10: 前后端联调
- 连接前端 API 调用到后端 `/api/tools/usage-monitor/analyze`
- 验证：点击"分析"按钮后，图表正确渲染
- 验证：时间过滤生效

**Ship/Show/Ask**: ❓ Ask（端到端验证）

---

### Task 11: 文档与收尾
- 更新 `openspec/design.md` 添加 Usage Monitor API 列表
- 更新 `.dev-workflow.md` 记录已知决策
- 更新 `README_CN.md` 工具列表
- Git commit + push

**Ship/Show/Ask**: 🚢 Ship
