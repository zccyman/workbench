# Tasks: Skills Manager

> 创建时间：2026-04-07
> 状态：待确认

## Task 1: 后端数据模型与扫描器 [L2]
**文件**：`backend/tools/skills_manager/models.py`, `scanner.py`
**内容**：
- Pydantic Skill 模型
- 分类映射配置 CATEGORIES
- 来源判断逻辑
- Scanner：扫描 `claw-skills/skills/` 目录，解析 SKILL.md 提取描述
**验证**：python -c "from scanner import scan_skills; print(len(scan_skills()))"

## Task 2: 后端数据库与状态持久化 [L2]
**文件**：`backend/tools/skills_manager/database.py`
**内容**：
- SQLite skill_status 表（skill_id, enabled, updated_at）
- get_status / set_status / toggle_status 函数
- 集成 workbench 现有 database.py 连接
**验证**：pytest tests/unit/backend/skills_manager/test_database.py

## Task 3: 后端 API 路由 [L3]
**文件**：`backend/tools/skills_manager/router.py`, `meta.json`
**内容**：
- GET /skills（列表，支持 category/search/source 查询参数）
- GET /skills/{skill_id}（详情，读取 SKILL.md 内容）
- PATCH /skills/{skill_id}/toggle（切换启用状态）
- GET /categories（分类统计）
- meta.json 工具元数据注册
**依赖**：Task 1, 2
**验证**：pytest tests/unit/backend/skills_manager/test_router.py

## Task 4: 前端技能管理页面 [L3]
**文件**：`frontend/src/pages/tools/SkillsManager.tsx`
**内容**：
- 分类展示（按类别分组，每组标题+卡片网格）
- 搜索框（实时过滤）
- 分类/来源筛选下拉
- 技能卡片（名称、描述、来源标签、文件数、启用状态、查看按钮）
- 详情弹窗（Markdown 渲染 SKILL.md + 启用/禁用开关）
- 统计栏（总数、已启用、分类数）
**依赖**：Task 3
**验证**：页面加载 → 搜索 → 筛选 → 查看详情 → 切换状态

## Task 5: 路由注册与集成测试 [L2]
**文件**：`frontend/src/App.tsx`（添加路由）, `frontend/src/components/Layout.tsx`（添加导航）
**内容**：
- App.tsx 注册 /tools/skills_manager 路由
- Layout 导航栏添加 Skills Manager 入口
- 端到端验证：启动 → 登录 → 访问技能页面 → 搜索 → 查看详情 → 切换状态
**依赖**：Task 4
**验证**：手动启动 start.sh，全流程验证
