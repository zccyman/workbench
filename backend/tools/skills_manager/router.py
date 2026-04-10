"""Skills Manager - API 路由"""

from fastapi import APIRouter

from .models import SkillDetail, SkillSummary, SkillsOverview, CategoryStats
from .scanner import scan_skills, get_skill_detail
from .database import get_enabled_map, toggle_skill
from .categories import CATEGORIES

router = APIRouter(tags=["skills-manager"])


def _skills_with_status() -> list[dict]:
    """获取带启用状态的技能列表"""
    skills = scan_skills()
    enabled_map = get_enabled_map()
    for s in skills:
        if s["id"] in enabled_map:
            s["enabled"] = enabled_map[s["id"]]
    return skills


@router.get("/skills", response_model=list[SkillSummary])
async def list_skills(
    category: str | None = None,
    search: str | None = None,
    source: str | None = None,
):
    """获取技能列表，支持筛选"""
    skills = _skills_with_status()

    if category:
        skills = [s for s in skills if s["category"] == category]
    if search:
        q = search.lower()
        skills = [
            s
            for s in skills
            if q in s["name"].lower() or q in s["description"].lower() or q in s["id"].lower()
        ]
    if source:
        skills = [s for s in skills if s["source"] == source]

    return [SkillSummary(**s) for s in skills]


@router.get("/skills/{skill_id}", response_model=SkillDetail)
async def get_skill(skill_id: str):
    """获取技能详情（含 SKILL.md 内容）"""
    detail = get_skill_detail(skill_id)
    if detail is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

    # 覆盖启用状态
    enabled_map = get_enabled_map()
    if detail["id"] in enabled_map:
        detail["enabled"] = enabled_map[detail["id"]]

    return SkillDetail(**detail)


@router.patch("/skills/{skill_id}/toggle")
async def toggle_skill_status(skill_id: str):
    """切换技能启用/禁用状态"""
    # 先确认技能存在
    detail = get_skill_detail(skill_id)
    if detail is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

    new_state = toggle_skill(skill_id)
    return {"skill_id": skill_id, "enabled": new_state}


@router.get("/categories", response_model=SkillsOverview)
async def get_categories():
    """获取分类统计"""
    skills = _skills_with_status()

    # 构建分类统计
    cat_stats = []
    for cat_key, cat_info in CATEGORIES.items():
        cat_skills = [s for s in skills if s["category"] == cat_key]
        cat_stats.append(
            CategoryStats(
                id=cat_key,
                name=cat_info["name"],
                icon=cat_info["icon"],
                count=len(cat_skills),
                enabled_count=sum(1 for s in cat_skills if s["enabled"]),
            )
        )

    # "其他"分类
    other_skills = [s for s in skills if s["category"] == "other"]
    if other_skills:
        cat_stats.append(
            CategoryStats(
                id="other",
                name="其他",
                icon="📦",
                count=len(other_skills),
                enabled_count=sum(1 for s in other_skills if s["enabled"]),
            )
        )

    return SkillsOverview(
        total=len(skills),
        enabled=sum(1 for s in skills if s["enabled"]),
        disabled=sum(1 for s in skills if not s["enabled"]),
        categories=cat_stats,
    )
