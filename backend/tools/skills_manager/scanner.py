"""Skills Manager - 技能目录扫描器"""

import os
from datetime import datetime

from .categories import CATEGORIES

# 数据源路径
SKILLS_ROOT = "/mnt/g/knowledge/claw-skills/skills"


def _get_category(skill_id: str) -> tuple[str, str, str]:
    """根据分类映射获取技能分类 (key, name, icon)，未匹配返回 'other'"""
    for cat_key, cat_info in CATEGORIES.items():
        if skill_id in cat_info["skills"]:
            return cat_key, cat_info["name"], cat_info["icon"]
    return "other", "其他", "📦"


def _detect_source(skill_id: str, skill_dir: str) -> str:
    """判断技能来源"""
    # 检查 SKILL.md 中是否包含自研标识
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_md):
        try:
            with open(skill_md, "r", encoding="utf-8") as f:
                head = f.read(2000)
                if "自研" in head or "self-developed" in head.lower():
                    return "自研"
        except Exception:
            pass
    # 默认标为开源
    return "开源"


def _extract_description(skill_md_path: str) -> str:
    """从 SKILL.md 提取第一段非标题描述"""
    if not os.path.exists(skill_md_path):
        return ""
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return ""

    # 跳过 frontmatter (---) 和标题行，取第一段正文
    in_frontmatter = False
    desc_lines = []
    started = False
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped.startswith("#"):
            if started and desc_lines:
                break  # 遇到下一个标题，停止
            continue
        if stripped == "":
            if started and desc_lines:
                break
            continue
        started = True
        desc_lines.append(stripped)

    return " ".join(desc_lines)[:200] if desc_lines else ""


def _extract_name(skill_id: str, skill_md_path: str) -> str:
    """从 SKILL.md 提取标题，否则用目录名"""
    if os.path.exists(skill_md_path):
        try:
            with open(skill_md_path, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("# ") and not stripped.startswith("# !"):
                        # 去掉 # 和前后空格
                        name = stripped[2:].strip()
                        if name:
                            return name
                    if stripped and not stripped.startswith("---"):
                        break
        except Exception:
            pass
    # 美化目录名：替换 - 为空格，首字母大写
    return skill_id.replace("-", " ").replace("_", " ").title()


def scan_skills() -> list[dict]:
    """扫描技能目录，返回技能信息列表"""
    skills = []

    if not os.path.isdir(SKILLS_ROOT):
        return skills

    for entry in sorted(os.listdir(SKILLS_ROOT)):
        skill_dir = os.path.join(SKILLS_ROOT, entry)
        if not os.path.isdir(skill_dir):
            continue

        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md_path):
            continue  # 没有 SKILL.md 的跳过

        # 统计文件数
        file_count = sum(
            1
            for _, _, files in os.walk(skill_dir)
            for f in files
            if not f.startswith(".")
        )

        # 最后修改时间
        try:
            mtime = os.path.getmtime(skill_dir)
            last_modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        except Exception:
            last_modified = ""

        cat_key, cat_name, cat_icon = _get_category(entry)
        source = _detect_source(entry, skill_dir)
        name = _extract_name(entry, skill_md_path)
        description = _extract_description(skill_md_path)

        skills.append(
            {
                "id": entry,
                "name": name,
                "description": description,
                "category": cat_key,
                "category_name": cat_name,
                "category_icon": cat_icon,
                "source": source,
                "enabled": True,  # 默认启用，后续由 database 覆盖
                "skill_md_path": skill_md_path,
                "file_count": file_count,
                "last_modified": last_modified,
            }
        )

    return skills


def get_skill_detail(skill_id: str) -> dict | None:
    """获取单个技能详情（含 SKILL.md 内容）"""
    skill_dir = os.path.join(SKILLS_ROOT, skill_id)
    if not os.path.isdir(skill_dir):
        return None

    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md_path):
        return None

    # 读取 SKILL.md 全文
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""

    # 获取基本信息
    all_skills = scan_skills()
    for s in all_skills:
        if s["id"] == skill_id:
            s["skill_md_content"] = content
            return s

    return None
