from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..database import get_db
from ..models import SessionWithProject, timestamp_to_str


def _fix_project_name(name, directory):
    """Fallback: use directory basename if name is null"""
    if name:
        return name
    if directory:
        return directory.rstrip('/').split('/')[-1] or directory
    return 'Unknown'


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionWithProject])
def list_sessions(
    source: str = Query("kilo", description="Data source: kilo or opencode"),
    project_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    db = get_db(source)

    query = """
        SELECT s.id, s.project_id, s.title, s.directory, s.time_created, s.time_updated,
               p.name as project_name,
               (SELECT COUNT(*) FROM message WHERE session_id = s.id) as message_count
        FROM session s
        LEFT JOIN project p ON s.project_id = p.id
    """
    params = []

    if project_id:
        query += " WHERE s.project_id = ?"
        params.append(project_id)

    query += " ORDER BY s.time_updated DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))

    sessions = []
    for row in rows:
        sessions.append(
            SessionWithProject(
                id=row[0],
                project_id=row[1],
                title=row[2],
                directory=row[3],
                time_created=row[4],
                time_updated=row[5],
                project_name=_fix_project_name(row[6], row[3]),
                message_count=row[7],
                time_created_str=timestamp_to_str(row[4]) if row[4] else None,
                time_updated_str=timestamp_to_str(row[5]) if row[5] else None,
            )
        )

    return sessions


@router.get("/{session_id}", response_model=SessionWithProject)
def get_session(
    session_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    query = """
        SELECT s.id, s.project_id, s.title, s.directory, s.time_created, s.time_updated,
               p.name as project_name,
               (SELECT COUNT(*) FROM message WHERE session_id = s.id) as message_count
        FROM session s
        LEFT JOIN project p ON s.project_id = p.id
        WHERE s.id = ?
    """
    row = db.execute_query_one(query, (session_id,))

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionWithProject(
        id=row[0],
        project_id=row[1],
        title=row[2],
        directory=row[3],
        time_created=row[4],
        time_updated=row[5],
        project_name=_fix_project_name(row[6], row[3]),
        message_count=row[7],
        time_created_str=timestamp_to_str(row[4]) if row[4] else None,
        time_updated_str=timestamp_to_str(row[5]) if row[5] else None,
    )


@router.get("/by-project/{project_id}", response_model=list[SessionWithProject])
def get_sessions_by_project(
    project_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    db = get_db(source)

    query = """
        SELECT s.id, s.project_id, s.title, s.directory, s.time_created, s.time_updated,
               p.name as project_name,
               (SELECT COUNT(*) FROM message WHERE session_id = s.id) as message_count
        FROM session s
        LEFT JOIN project p ON s.project_id = p.id
        WHERE s.project_id = ?
        ORDER BY s.time_updated DESC
        LIMIT ? OFFSET ?
    """
    rows = db.execute_query(query, (project_id, limit, offset))

    sessions = []
    for row in rows:
        sessions.append(
            SessionWithProject(
                id=row[0],
                project_id=row[1],
                title=row[2],
                directory=row[3],
                time_created=row[4],
                time_updated=row[5],
                project_name=_fix_project_name(row[6], row[3]),
                message_count=row[7],
                time_created_str=timestamp_to_str(row[4]) if row[4] else None,
                time_updated_str=timestamp_to_str(row[5]) if row[5] else None,
            )
        )

    return sessions


@router.get("/by-date/{date}", response_model=list[SessionWithProject])
def get_sessions_by_date(
    date: str, source: str = Query("kilo", description="Data source: kilo or opencode")
):
    db = get_db(source)

    ts = int(date) if date.isdigit() else 0
    start_ts = ts
    end_ts = ts + 86400000

    query = """
        SELECT s.id, s.project_id, s.title, s.directory, s.time_created, s.time_updated,
               p.name as project_name,
               (SELECT COUNT(*) FROM message WHERE session_id = s.id) as message_count
        FROM session s
        LEFT JOIN project p ON s.project_id = p.id
        WHERE s.time_created >= ? AND s.time_created < ?
        ORDER BY s.time_updated DESC
    """
    rows = db.execute_query(query, (start_ts, end_ts))

    sessions = []
    for row in rows:
        sessions.append(
            SessionWithProject(
                id=row[0],
                project_id=row[1],
                title=row[2],
                directory=row[3],
                time_created=row[4],
                time_updated=row[5],
                project_name=_fix_project_name(row[6], row[3]),
                message_count=row[7],
                time_created_str=timestamp_to_str(row[4]) if row[4] else None,
                time_updated_str=timestamp_to_str(row[5]) if row[5] else None,
            )
        )

    return sessions
