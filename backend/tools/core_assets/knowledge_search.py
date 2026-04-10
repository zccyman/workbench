"""Core Assets - 知识库搜索，自动补充描述"""

import json
import subprocess
from pathlib import Path

WIKI_DIR = Path("/mnt/g/knowledge/wiki/topics")
INDEX_DIR = Path("/mnt/g/knowledge/claw-mem/knowledge_index")


def search_wiki(query: str, limit: int = 3) -> list[dict]:
    """搜索 Wiki 知识库，返回相关文档"""
    results = []

    # 先尝试 Whoosh 索引
    try:
        from whoosh.index import open_dir
        from whoosh.qparser import QueryParser

        ix = open_dir(str(INDEX_DIR))
        with ix.searcher() as searcher:
            qp = QueryParser("content", ix.schema)
            q = qp.parse(query)
            hits = searcher.search(q, limit=limit)
            for hit in hits:
                results.append({
                    "title": hit.get("title", ""),
                    "path": hit.get("path", ""),
                    "score": hit.score,
                })
    except Exception:
        pass

    # 回退：文件名匹配
    if not results:
        q = query.lower()
        for f in WIKI_DIR.glob("*.md"):
            if q in f.stem.lower() or q in f.name.lower():
                # 读取前200字作为描述
                try:
                    content = f.read_text(encoding="utf-8")[:200]
                except Exception:
                    content = ""
                results.append({
                    "title": f.stem,
                    "path": str(f),
                    "snippet": content,
                })
                if len(results) >= limit:
                    break

    return results


def auto_fill_description(name: str) -> dict:
    """根据名字自动搜索知识库，补充描述和建议"""
    results = search_wiki(name, limit=3)
    description = ""
    tags = []
    category = "general"

    if results:
        # 用第一个结果的片段作为描述基础
        r = results[0]
        snippet = r.get("snippet", r.get("title", ""))
        if snippet:
            description = f"（自动从知识库补充）{snippet[:150]}"

    # 简单分类推断
    name_lower = name.lower()
    if any(kw in name_lower for kw in ["workflow", "dev", "code", "develop"]):
        category = "开发工具"
        tags.append("开发")
    elif any(kw in name_lower for kw in ["search", "search"]):
        category = "搜索"
        tags.append("搜索")
    elif any(kw in name_lower for kw in ["agent", "bot", "智能体"]):
        category = "智能体"
        tags.append("AI")
    elif any(kw in name_lower for kw in ["memory", "知识", "knowledge"]):
        category = "知识库"
        tags.append("知识管理")
    elif any(kw in name_lower for kw in ["content", "文章", "公众号"]):
        category = "内容"
        tags.append("内容生成")

    return {
        "description": description,
        "category": category,
        "tags": tags,
        "wiki_matches": results,
        "auto_filled": bool(results),
    }
