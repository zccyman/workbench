import json
from typing import List, Dict, Optional
from ..database import get_db
from ..models import KnowledgeExtraction

knowledge_cache: Dict[str, KnowledgeExtraction] = {}


def extract_knowledge(session_id: str, source: str = "kilo") -> KnowledgeExtraction:
    """Extract knowledge from a session."""
    cache_key = f"{source}:{session_id}"
    if cache_key in knowledge_cache:
        return knowledge_cache[cache_key]

    db = get_db(source)

    session = db.execute_query_one(
        "SELECT title, directory FROM session WHERE id = ?", (session_id,)
    )

    if not session:
        return KnowledgeExtraction(session_id=session_id)

    messages_query = """
        SELECT data FROM message
        WHERE session_id = ?
        ORDER BY time_created ASC
    """
    message_rows = db.execute_query(messages_query, (session_id,))

    content_parts = []
    for row in message_rows:
        try:
            parsed = json.loads(row[0])
            role = parsed.get("role", "")
            content = parsed.get("content", "")
            if content:
                content_parts.append(f"[{role.upper()}]: {content}")
        except:
            pass

    full_content = "\n\n".join(content_parts[:10])

    technical_solutions = _extract_technical_solutions(full_content)
    decisions = _extract_decisions(full_content)
    lessons_learned = _extract_lessons(full_content)
    key_files = _extract_key_files(full_content)

    result = KnowledgeExtraction(
        session_id=session_id,
        technical_solutions=technical_solutions,
        decisions=decisions,
        lessons_learned=lessons_learned,
        key_files=key_files,
    )

    knowledge_cache[cache_key] = result
    return result


def _extract_technical_solutions(content: str) -> List[str]:
    keywords = [
        "solution",
        "fix",
        "implementation",
        "code",
        "function",
        "class",
        "method",
    ]
    solutions = []

    lines = content.split("\n")
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw in line_lower for kw in keywords):
            if len(line) > 10 and len(solutions) < 5:
                solutions.append(line.strip()[:100])

    return solutions[:5]


def _extract_decisions(content: str) -> List[str]:
    keywords = [
        "decided",
        "choose",
        "use",
        "adopt",
        "implement",
        "design",
        "architecture",
    ]
    decisions = []

    lines = content.split("\n")
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in keywords):
            if len(line) > 10 and len(decisions) < 5:
                decisions.append(line.strip()[:100])

    return decisions[:5]


def _extract_lessons(content: str) -> List[str]:
    keywords = ["learned", "note", "important", "remember", "tip", "better"]
    lessons = []

    lines = content.split("\n")
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in keywords):
            if len(line) > 10 and len(lessons) < 5:
                lessons.append(line.strip()[:100])

    return lessons[:5]


def _extract_key_files(content: str) -> List[str]:
    import re

    file_pattern = r"[a-zA-Z0-9_\-/]+\.[a-zA-Z]+"
    files = re.findall(file_pattern, content)

    common_extensions = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".md",
        ".yml",
        ".yaml",
        ".sh",
        ".html",
        ".css",
    }
    key_files = []

    for f in files:
        if any(f.endswith(ext) for ext in common_extensions):
            if f not in key_files:
                key_files.append(f)

    return key_files[:10]


def clear_cache():
    """Clear the knowledge cache."""
    global knowledge_cache
    knowledge_cache = {}
