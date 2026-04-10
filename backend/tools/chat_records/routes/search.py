from fastapi import APIRouter, Query
from typing import List
from ..database import db
from ..models import SearchResult

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=List[SearchResult])
def search_messages(
    q: str = Query(..., description="Search query"),
    platform: str = Query("wechat"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    search_term = f"%{q}%"

    query = """
        SELECT m.id, m.conversation_id, m.platform, m.sender_name,
               m.content, m.timestamp
        FROM chat_message m
        WHERE m.platform = ? AND m.content LIKE ?
        ORDER BY m.timestamp DESC
        LIMIT ? OFFSET ?
    """
    rows = db.execute_query(query, (platform, search_term, limit, offset))

    results = []
    for r in rows:
        content = r["content"] or ""
        snippet = content[:200] + "..." if len(content) > 200 else content
        results.append(
            SearchResult(
                message_id=r["id"],
                conversation_id=r["conversation_id"],
                platform=r["platform"],
                sender_name=r["sender_name"],
                snippet=snippet,
                timestamp=r["timestamp"],
                highlights=[q],
            )
        )

    return results


@router.get("/fts", response_model=List[SearchResult])
def search_fts(
    q: str = Query(..., description="Search query"),
    platform: str = Query("wechat"),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        query = """
            SELECT m.id, m.conversation_id, m.platform, m.sender_name,
                   m.content, m.timestamp,
                   snippet(chat_message_fts, '[', ']', '...', 1, 32) as snippet_text
            FROM chat_message_fts fts
            JOIN chat_message m ON m.rowid = fts.rowid
            WHERE chat_message_fts MATCH ? AND m.platform = ?
            ORDER BY rank
            LIMIT ?
        """
        rows = db.execute_query(query, (q, platform, limit))

        results = []
        for r in rows:
            results.append(
                SearchResult(
                    message_id=r["id"],
                    conversation_id=r["conversation_id"],
                    platform=r["platform"],
                    sender_name=r["sender_name"],
                    snippet=r["snippet_text"] or r["content"][:200]
                    if r["content"]
                    else "",
                    timestamp=r["timestamp"],
                    highlights=[q],
                )
            )
        return results
    except Exception:
        return search_messages(q, platform, limit)
