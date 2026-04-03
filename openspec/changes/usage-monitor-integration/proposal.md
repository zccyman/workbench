# Usage Monitor Integration — Proposal

> 版本：1.0.0 | 创建：2026-04-04 | 状态：Draft

## 做什么

将 `openclaw-usage-monitor`（TypeScript CLI 工具）以 Python FastAPI 工具形式入驻 workbench，作为 `backend/tools/usage_monitor/`，并配套前端可视化页面。

## 为什么

1. **统一工具入口** — workbench 是个人工具箱，usage-monitor 是日常高频使用的开发分析工具，理应集成
2. **可视化升级** — 原 CLI 的终端表格输出改为前端图表（recharts），更直观
3. **Web 化** — 从 CLI 命令行改为浏览器访问，无需终端即可生成使用报告

## 迁移范围

| 模块 | 来源 | 目标 | 方式 |
|------|------|------|------|
| collector.ts | `openclaw-usage-monitor/src/collector.ts` | `backend/tools/usage_monitor/collector.py` | 重写为 Python |
| analyzer.ts | `openclaw-usage-monitor/src/analyzer.ts` | `backend/tools/usage_monitor/analyzer.py` | 重写为 Python |
| reporter.ts | `openclaw-usage-monitor/src/reporter.ts` | `backend/tools/usage_monitor/reporter.py` | 重写为 Python（保留 markdown/json 输出） |
| types.ts | `openclaw-usage-monitor/src/types.ts` | `backend/tools/usage_monitor/models.py` | Pydantic models |
| CLI 界面 | `openclaw-usage-monitor/src/cli.ts` | `frontend/src/pages/tools/UsageMonitor.tsx` | 改为 React 页面 |

## 暂不迁移

| 模块 | 原因 |
|------|------|
| CLI 参数解析（commander） | 改为前端 UI 控件（下拉框、日期选择器） |
| cli-table3 终端表格 | 前端用 recharts 图表替代 |
| `bin` 入口 | 不再需要 CLI 入口，通过 Web API 调用 |

## 目录结构草案

```
backend/tools/usage_monitor/
├── __init__.py
├── meta.json
├── router.py              # FastAPI APIRouter
├── models.py              # Pydantic 请求/响应模型
├── collector.py           # JSONL 文件解析（重写自 collector.ts）
├── analyzer.py            # 数据分析逻辑（重写自 analyzer.ts）
└── reporter.py            # 报告格式化（markdown/json）

frontend/src/pages/tools/
└── UsageMonitor.tsx       # 可视化页面

frontend/src/components/usage_monitor/
├── ConfigPanel.tsx        # 配置面板（目录、Agent、时间过滤）
├── ToolFrequencyChart.tsx # 工具使用频率柱状图
├── SkillFrequencyChart.tsx# 技能激活频率柱状图
├── HourlyHeatmap.tsx      # 24小时分布图
├── DailyActivityChart.tsx # 每日活跃度折线图
└── SummaryCards.tsx       # 汇总卡片（Sessions/Tool Calls/Skill Reads）

tests/unit/backend/usage_monitor/
├── test_collector.py
├── test_analyzer.py
└── test_router.py
```

## 原始项目保护

原 `openclaw-usage-monitor` 项目保持不变，不做任何修改。workbench 中的代码为独立重写版本。
