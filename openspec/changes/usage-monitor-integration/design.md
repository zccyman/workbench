# Usage Monitor Integration — Design Spec

> 版本：1.0.0 | 创建：2026-04-04 | 状态：Draft

## 1. 架构概览

```
用户浏览器 → UsageMonitor.tsx → GET/POST /api/tools/usage-monitor/* → collector.py → JSONL 文件解析
                                                        ↓
                                                  analyzer.py → 数据分析
                                                        ↓
                                                  reporter.py → 报告格式化
```

## 2. 后端设计

### 2.1 目录结构

```
backend/tools/usage_monitor/
├── __init__.py
├── meta.json
├── router.py              # API 路由
├── models.py              # Pydantic models
├── collector.py           # JSONL 解析器
├── analyzer.py            # 数据分析器
└── reporter.py            # 报告格式化器
```

### 2.2 meta.json

```json
{
  "name": "Usage Monitor",
  "id": "usage_monitor",
  "description": "OpenClaw 会话使用数据分析工具，跟踪工具调用、技能激活、时间分布",
  "icon": "📊",
  "category": "开发工具",
  "version": "1.0.0"
}
```

### 2.3 models.py（Pydantic）

```python
from pydantic import BaseModel
from typing import Dict, List, Optional

class AnalysisRequest(BaseModel):
    agent_dir: str = ""           # OpenClaw agents 目录，空则用默认路径
    agent_name: str = "bot1"      # Agent 名称
    from_date: Optional[str] = None  # YYYY-MM-DD
    to_date: Optional[str] = None    # YYYY-MM-DD
    period: str = "all"             # daily|weekly|monthly|all

class SummaryResponse(BaseModel):
    total_sessions: int
    total_tool_calls: int
    total_skill_reads: int
    date_range_from: str
    date_range_to: str

class ToolUsageItem(BaseModel):
    rank: int
    tool_name: str
    calls: int
    percentage: float

class SkillUsageItem(BaseModel):
    rank: int
    skill_name: str
    activations: int

class HourlyDataItem(BaseModel):
    hour: int
    calls: int

class DailyActivityItem(BaseModel):
    date: str
    sessions: int
    tool_calls: int
    skill_reads: int

class AnalysisResponse(BaseModel):
    summary: SummaryResponse
    tool_frequency: List[ToolUsageItem]
    skill_frequency: List[SkillUsageItem]
    hourly_distribution: List[HourlyDataItem]
    daily_activity: List[DailyActivityItem]

class MarkdownReportResponse(BaseModel):
    content: str
```

### 2.4 collector.py（重写自 collector.ts）

核心逻辑：
1. 扫描 `{agent_dir}/sessions/` 下所有 `.jsonl` 文件
2. 逐行解析 JSON，提取 `type=message` + `role=assistant` 的事件
3. 从 `content[].type=toolCall` 提取工具调用
4. 检测 `read` 工具的 `SKILL.md` 路径，提取技能名
5. 返回 `tool_calls`, `skill_reads`, `sessions` 三个列表

关键差异（vs TypeScript）：
- 使用 `pathlib` 处理路径
- 使用 `json` 模块逐行解析
- 默认路径：`~/.openclaw/agents/bot1`（同原 CLI）

### 2.5 analyzer.py（重写自 analyzer.ts）

核心逻辑：
1. 工具使用频率统计（Counter）
2. 技能激活频率统计
3. 24 小时分布（按 timestamp 提取 hour）
4. 每日活跃度（按日期聚合 sessions/tool_calls/skill_reads）
5. 支持 period 过滤（daily/weekly/monthly/all）

### 2.6 reporter.py

保留 markdown 和 json 两种输出格式，供前端导出使用。

### 2.7 router.py（API 路由）

```
GET  /analyze?agent_dir=&agent_name=bot1&from_date=&to_date=&period=all
     → 执行完整的分析流程，返回 AnalysisResponse

POST /analyze
     → 接收 AnalysisRequest，返回 AnalysisResponse

GET  /report/markdown?period=all
     → 返回 MarkdownReportResponse

GET  /config
     → 返回默认配置（默认 agent 目录等）
```

## 3. 前端设计

### 3.1 页面结构

```
UsageMonitor.tsx（主页面）
├── ConfigPanel（顶部配置区）
│   ├── Agent 选择下拉框
│   ├── 时间范围选择（all/daily/weekly/monthly）
│   ├── 自定义日期范围选择器
│   └── "分析" 按钮
├── SummaryCards（汇总卡片）
│   ├── Sessions 数量
│   ├── Tool Calls 数量
│   └── Skill Reads 数量
├── ToolFrequencyChart（工具使用频率柱状图）
├── SkillFrequencyChart（技能激活频率柱状图）
├── HourlyHeatmap（24 小时分布热力图）
└── DailyActivityChart（每日活跃度折线图）
```

### 3.2 依赖

| 包 | 用途 | 已安装？ |
|----|------|---------|
| recharts | 图表渲染 | ✅（AI Session Manager 已引入） |
| date-fns | 日期处理 | ✅（AI Session Manager 已引入） |
| lucide-react | 图标 | ✅（AI Session Manager 已引入） |

无需新增依赖。

### 3.3 Import 路径映射

```
frontend/src/pages/tools/UsageMonitor.tsx
  → import from '../../components/usage_monitor/...'
  → import from '../../utils/api' (已有)
```

## 4. Import 路径映射表

| 源文件 | 目标文件 |
|--------|---------|
| `collector.ts` | `backend/tools/usage_monitor/collector.py` |
| `analyzer.ts` | `backend/tools/usage_monitor/analyzer.py` |
| `reporter.ts` | `backend/tools/usage_monitor/reporter.py` |
| `types.ts` | `backend/tools/usage_monitor/models.py` |
| `cli.ts` | 拆分为 `router.py` + `UsageMonitor.tsx` |

## 5. 风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| JSONL 文件格式变化 | 解析失败 | 添加容错处理，跳过无法解析的行 |
| 大文件性能 | 分析慢 | 提示用户时间范围过滤，异步处理 |
| 路径权限问题 | 无法读取 | 返回清晰的错误信息 |
