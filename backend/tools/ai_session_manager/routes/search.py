from fastapi import APIRouter, Query, HTTPException
from typing import List
import json
from .database import get_db
from .models import SearchResult

router = APIRouter(prefix="/search", tags=["search"])


def parse_message_data(data: str) -> dict:
    """Parse the data field from message which is a JSON string."""
    try:
        return json.loads(data)
    except:
        return {}


@router.get("", response_model=List[SearchResult])
def search_sessions(
    q: str = Query(..., description="Search query"),
    source: str = Query("kilo", description="Data source: kilo or opencode"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    db = get_db(source)

    search_term = f"%{q}%"

    query = """
        SELECT DISTINCT s.id as session_id, s.title as session_title, m.id as message_id
        FROM session s
        JOIN message m ON s.id = m.session_id
        WHERE s.title LIKE ? OR m.data LIKE ?
        LIMIT ? OFFSET ?
    """
    rows = db.execute_query(query, (search_term, search_term, limit, offset))

    results = []
    for row in rows:
        message_query = "SELECT data FROM message WHERE id = ?"
        message_row = db.execute_query_one(message_query, (row[2],))

        snippet = ""
        if message_row:
            parsed = parse_message_data(message_row[0])
            content = parsed.get("content", "")
            if content:
                snippet = content[:200] + "..." if len(content) > 200 else content

        results.append(
            SearchResult(
                session_id=row[0],
                session_title=row[1],
                message_id=row[2],
                snippet=snippet,
                highlights=[q],
            )
        )

    return results


@router.get("/sessions/{session_id}", response_model=List[SearchResult])
def search_in_session(
    session_id: str,
    q: str = Query(..., description="Search query"),
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    search_term = f"%{q}%"

    query = """
        SELECT s.id as session_id, s.title as session_title, m.id as message_id
        FROM session s
        JOIN message m ON s.id = m.session_id
        WHERE s.id = ? AND m.data LIKE ?
    """
    rows = db.execute_query(query, (session_id, search_term))

    results = []
    for row in rows:
        message_query = "SELECT data FROM message WHERE id = ?"
        message_row = db.execute_query_one(message_query, (row[2],))

        snippet = ""
        if message_row:
            parsed = parse_message_data(message_row[0])
            content = parsed.get("content", "")
            if content:
                snippet = content[:200] + "..." if len(content) > 200 else content

        results.append(
            SearchResult(
                session_id=row[0],
                session_title=row[1],
                message_id=row[2],
                snippet=snippet,
                highlights=[q],
            )
        )

    return results
