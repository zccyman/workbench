# Design: Skills Manager

> 创建时间：2026-04-07
> 状态：待确认

## 架构概览

```
claw-skills/skills/          ← 数据源（文件系统）
        ↓
backend/tools/skills_manager/
  ├── router.py              ← API 路由（4个端点）
  ├── meta.json              ← 工具元数据
  ├── scanner.py             ← 扫描技能目录
  ├── models.py              ← Pydantic 模型
  └── database.py            ← SQLite 状态持久化
        ↓
frontend/src/pages/tools/SkillsManager.tsx   ← 管理页面
```

## 数据模型

### Skill（技能）

```python
class Skill(BaseModel):
    id: str                    # 目录名（如 "dev-workflow"）
    name: str                  # 显示名称
    description: str           # SKILL.md 第一段描述
    category: str              # 分类（开发工具/搜索/内容生成/AI知识库/系统工具/智能体）
    source: str                # 来源（自研/开源/系统内置）
    enabled: bool              # 启用状态
    skill_md_path: str         # SKILL.md 完整路径
    file_count: int            # 目录下文件数
    last_modified: str         # 最后修改时间
```

### 分类映射（硬编码配置）

```python
CATEGORIES = {
    "dev-tools": {"name": "开发工具", "icon": "🔧", "skills": [
        "dev-workflow", "skill-forge-eval", "autoskill", "planning-with-files"
    ]},
    "search": {"name": "搜索", "icon": "🔍", "skills": [
        "tabbit-search", "web-search", "multi-search-engine", "find-skills"
    ]},
    "content": {"name": "内容生成", "icon": "📝", "skills": [
        "wechat-docx-export", "wechat-mp-content-agent", "douyin-video-from-docx",
        "english-learning", "github-trending-monitor", "global-news-monitor"
    ]},
    "ai-knowledge": {"name": "AI/知识库", "icon": "🧠", "skills": [
        "knowledge-qa", "karpathy-knowledge-base", "ontology",
        "knowledge-archiver", "knowledge-value-assessment", "wiki-qa", "goskills"
    ]},
    "system": {"name": "系统工具", "icon": "🛠️", "skills": [
        "bleachbit", "disk-analyzer", "model-downloader", "simple-cleanup",
        "simplify", "opencli-rs", "obsidian"
    ]},
    "agent": {"name": "智能体", "icon": "🤖", "skills": [
        "agent-browser", "task-dispatcher", "self-improving", "self-evolution",
        "free-ride", "a股市场情绪监控"
    ]},
}
```

### 来源判断规则

| 规则 | 来源标签 |
|------|---------|
| SKILL.md 中含 "自研" 或目录在 claw-skills 原始创建 | 自研 |
| 目录在其他系统路径（如 ~/.openclaw/skills/、~/.agents/skills/） | 系统内置 |
| 其他 | 开源 |

## API 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tools/skills-manager/skills` | 获取技能列表（支持 `?category=&search=&source=` 筛选） |
| GET | `/api/tools/skills-manager/skills/{skill_id}` | 获取技能详情（含 SKILL.md 内容） |
| PATCH | `/api/tools/skills-manager/skills/{skill_id}/toggle` | 切换启用/禁用 |
| GET | `/api/tools/skills-manager/categories` | 获取分类统计 |

## 前端设计

### 页面布局

```
┌─────────────────────────────────────────┐
│ 🔍 搜索框          [分类筛选▼] [来源▼]  │
├─────────────────────────────────────────┤
│ 📊 统计栏：总计 37 | 已启用 35 | 6个分类 │
├─────────────────────────────────────────┤
│ 🔧 开发工具 (4)                         │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
│ │卡 片1│ │卡 片2│ │卡 片3│ │卡 片4│   │
│ └──────┘ └──────┘ └──────┘ └──────┘   │
│ 🔍 搜索 (4)                             │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
│ │      │ │      │ │      │ │      │   │
│ └──────┘ └──────┘ └──────┘ └──────┘   │
│ ...                                     │
└─────────────────────────────────────────┘
```

### 技能卡片

```
┌──────────────────────────┐
│ 🔧 dev-workflow     [自研]│
│ AI驱动开发工作流          │
│ 📄 15文件 | 04-07更新     │
│ [🟢 已启用] [查看详情]    │
└──────────────────────────┘
```

### 详情弹窗（Modal）

展示完整 SKILL.md 内容（Markdown 渲染）+ 元数据 + 启用/禁用开关

## 状态持久化

启用/禁用状态存储在 workbench.db 的 `skill_status` 表中：

```sql
CREATE TABLE IF NOT EXISTS skill_status (
    skill_id TEXT PRIMARY KEY,
    enabled BOOLEAN DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

新增技能（不在数据库中）默认为启用。
