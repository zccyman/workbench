"""Skills Manager - Pydantic 数据模型"""

from pydantic import BaseModel


class Skill(BaseModel):
    """技能模型"""

    id: str  # 目录名（如 "dev-workflow"）
    name: str  # 显示名称（取自目录名或 SKILL.md 标题）
    description: str  # SKILL.md 第一段描述
    category: str  # 分类 key（如 "dev-tools"）
    category_name: str  # 分类中文名
    category_icon: str  # 分类图标
    source: str  # 来源：自研/开源/系统内置
    enabled: bool  # 启用状态
    skill_md_path: str  # SKILL.md 完整路径
    file_count: int  # 目录下文件数
    last_modified: str  # 最后修改时间（ISO格式）


class SkillSummary(BaseModel):
    """技能列表摘要（不含 SKILL.md 内容）"""

    id: str
    name: str
    description: str
    category: str
    category_name: str
    category_icon: str
    source: str
    enabled: bool
    file_count: int
    last_modified: str


class SkillDetail(SkillSummary):
    """技能详情（含 SKILL.md 内容）"""

    skill_md_content: str = ""


class CategoryStats(BaseModel):
    """分类统计"""

    id: str
    name: str
    icon: str
    count: int
    enabled_count: int


class SkillsOverview(BaseModel):
    """技能总览"""

    total: int
    enabled: int
    disabled: int
    categories: list[CategoryStats]
