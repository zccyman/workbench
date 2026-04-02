import json
from typing import List, Dict, Optional
from ..database import get_db
from ..models import SearchResult


def search_sessions(
    query: str, source: str = "kilo", limit: int = 20, offset: int = 0
) -> List[SearchResult]:
    """Full-text search across sessions and messages."""
    db = get_db(source)

    search_term = f"%{query}%"

    sql = """
        SELECT DISTINCT s.id as session_id, s.title as session_title, m.id as message_id
        FROM session s
        JOIN message m ON s.id = m.session_id
        WHERE s.title LIKE ? OR m.data LIKE ?
        LIMIT ? OFFSET ?
    """
    rows = db.execute_query(sql, (search_term, search_term, limit, offset))

    results = []
    for row in rows:
        message_row = db.execute_query_one(
            "SELECT data FROM message WHERE id = ?", (row[2],)
        )

        snippet = ""
        if message_row:
            try:
                parsed = json.loads(message_row[0])
                content = parsed.get("content", "")
                if content:
                    snippet = content[:200] + "..." if len(content) > 200 else content
            except:
                pass

        results.append(
            SearchResult(
                session_id=row[0],
                session_title=row[1],
                message_id=row[2],
                snippet=snippet,
                highlights=[query],
            )
        )

    return results


def search_in_session(
    session_id: str, query: str, source: str = "kilo"
) -> List[SearchResult]:
    """Search within a specific session."""
    db = get_db(source)

    search_term = f"%{query}%"

    sql = """
        SELECT s.id as session_id, s.title as session_title, m.id as message_id
        FROM session s
        JOIN message m ON s.id = m.session_id
        WHERE s.id = ? AND m.data LIKE ?
    """
    rows = db.execute_query(sql, (session_id, search_term))

    results = []
    for row in rows:
        message_row = db.execute_query_one(
            "SELECT data FROM message WHERE id = ?", (row[2],)
        )

        snippet = ""
        if message_row:
            try:
                parsed = json.loads(message_row[0])
                content = parsed.get("content", "")
                if content:
                    snippet = content[:200] + "..." if len(content) > 200 else content
            except:
                pass

        results.append(
            SearchResult(
                session_id=row[0],
                session_title=row[1],
                message_id=row[2],
                snippet=snippet,
                highlights=[query],
            )
        )

    return results
