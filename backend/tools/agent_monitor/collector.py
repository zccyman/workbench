import os
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..ai_session_manager.config import config
from ..ai_session_manager.database import get_database
from ..ai_session_manager.models import timestamp_to_str

MODEL_DEFAULT_TOKENS_PER_MESSAGE = 500


def _detect_model_from_session(session_row) -> Optional[str]:
    """Extract model info from session title or directory if available."""
    title = getattr(session_row, "title", "") or (
        session_row["title"] if isinstance(session_row, dict) else ""
    )
    directory = getattr(session_row, "directory", "") or (
        session_row["directory"] if isinstance(session_row, dict) else ""
    )

    for keyword in ("claude", "sonnet", "opus"):
        if keyword in title.lower() or keyword in directory.lower():
            return f"claude-{keyword}"

    for keyword in ("glm", "zhipu"):
        if keyword in title.lower() or keyword in directory.lower():
            return "glm-4.7"

    for keyword in ("gpt", "codex", "openai"):
        if keyword in title.lower() or keyword in directory.lower():
            return "gpt-5.3-codex"

    for keyword in ("gemini", "google"):
        if keyword in title.lower() or keyword in directory.lower():
            return "gemini-2.5-pro"

    return None


def _get_sessions_from_source(
    source: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
) -> list[dict]:
    """Query sessions from a single source (kilo or opencode)."""
    try:
        db = get_database(source)
    except Exception:
        return []

    query = """
        SELECT s.id, s.project_id, s.title, s.directory, s.time_created, s.time_updated,
               p.name as project_name,
               (SELECT COUNT(*) FROM message WHERE session_id = s.id) as message_count
        FROM session s
        LEFT JOIN project p ON s.project_id = p.id
    """
    params = []
    conditions = []

    if date_from:
        try:
            ts_from = int(datetime.fromisoformat(date_from).timestamp())
            conditions.append("s.time_created >= ?")
            params.append(ts_from)
        except (ValueError, OSError):
            pass

    if date_to:
        try:
            ts_to = int(
                (datetime.fromisoformat(date_to) + timedelta(days=1)).timestamp()
            )
            conditions.append("s.time_created < ?")
            params.append(ts_to)
        except (ValueError, OSError):
            pass

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY s.time_updated DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))
    sessions = []

    for row in rows:
        model = _detect_model_from_session(row)
        sessions.append(
            {
                "session_id": row[0],
                "project_id": row[1],
                "title": row[2],
                "directory": row[3],
                "project_name": row[6]
                or (row[3].rstrip("/").split("/")[-1] if row[3] else "Unknown"),
                "agent_type": source,
                "model": model,
                "time_created": row[4],
                "time_updated": row[5],
                "start_time": timestamp_to_str(row[4]) if row[4] else None,
                "end_time": timestamp_to_str(row[5]) if row[5] else None,
                "message_count": row[7],
            }
        )

    return sessions


def _get_total_count(
    source: str, date_from: Optional[str] = None, date_to: Optional[str] = None
) -> int:
    """Get total session count for a source with optional date filters."""
    try:
        db = get_database(source)
    except Exception:
        return 0

    query = "SELECT COUNT(*) FROM session"
    params = []
    conditions = []

    if date_from:
        try:
            ts_from = int(datetime.fromisoformat(date_from).timestamp())
            conditions.append("time_created >= ?")
            params.append(ts_from)
        except (ValueError, OSError):
            pass

    if date_to:
        try:
            ts_to = int(
                (datetime.fromisoformat(date_to) + timedelta(days=1)).timestamp()
            )
            conditions.append("time_created < ?")
            params.append(ts_to)
        except (ValueError, OSError):
            pass

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    result = db.execute_query_one(query, tuple(params))
    return result[0] if result else 0


def _get_session_detail(source: str, session_id: str) -> Optional[dict]:
    """Get single session detail with message count."""
    try:
        db = get_database(source)
    except Exception:
        return None

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
        return None

    return {
        "session_id": row[0],
        "project_id": row[1],
        "title": row[2],
        "directory": row[3],
        "project_name": row[6]
        or (row[3].rstrip("/").split("/")[-1] if row[3] else "Unknown"),
        "agent_type": source,
        "model": _detect_model_from_session(row),
        "time_created": row[4],
        "time_updated": row[5],
        "start_time": timestamp_to_str(row[4]) if row[4] else None,
        "end_time": timestamp_to_str(row[5]) if row[5] else None,
        "message_count": row[7],
    }


def _check_process_running(name_pattern: str) -> bool:
    """Check if a process matching the pattern is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", name_pattern],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def _get_recent_active_count(source: str, minutes: int = 5) -> int:
    """Count sessions active in the last N minutes."""
    try:
        db = get_database(source)
    except Exception:
        return 0

    cutoff = int((datetime.now() - timedelta(minutes=minutes)).timestamp())
    query = "SELECT COUNT(*) FROM session WHERE time_updated >= ?"
    result = db.execute_query_one(query, (cutoff,))
    return result[0] if result else 0


def _get_last_active_time(source: str) -> Optional[str]:
    """Get the most recent session update time."""
    try:
        db = get_database(source)
    except Exception:
        return None

    query = "SELECT MAX(time_updated) FROM session"
    result = db.execute_query_one(query)
    if result and result[0]:
        return timestamp_to_str(result[0])
    return None


def _get_most_used_model(source: str) -> Optional[str]:
    """Get the most frequently used model for a source (based on session count)."""
    sessions = _get_sessions_from_source(source, limit=100)
    if not sessions:
        return None

    model_counts: dict[str, int] = {}
    for s in sessions:
        model = s.get("model") or "unknown"
        model_counts[model] = model_counts.get(model, 0) + 1

    if not model_counts:
        return None

    return max(model_counts, key=model_counts.get)


def collect_all_data(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
) -> dict:
    """Collect unified data from both KiloCode and OpenCode sources.

    Returns:
        {
            "sessions": [...],
            "total": int,
            "sources": ["kilo", "opencode"],
        }
    """
    all_sessions = []
    total = 0
    sources = []

    for source in ["kilo", "opencode"]:
        db_path = config.get_db_path(source)
        if not os.path.exists(db_path):
            continue

        sources.append(source)
        sessions = _get_sessions_from_source(source, date_from, date_to, limit, offset)
        all_sessions.extend(sessions)
        total += _get_total_count(source, date_from, date_to)

    all_sessions.sort(key=lambda s: s.get("time_updated", 0) or 0, reverse=True)

    return {
        "sessions": all_sessions[:limit],
        "total": total,
        "sources": sources,
    }


def collect_agent_status() -> list[dict]:
    """Collect status for each agent type."""
    agents = []

    for source, name, pattern in [
        ("kilocode", "KiloCode", "kilo"),
        ("opencode", "OpenCode", "opencode"),
    ]:
        db_path = config.get_db_path(source)
        process_running = os.path.exists(db_path) and _check_process_running(pattern)
        active_sessions = _get_recent_active_count(source, minutes=5)
        last_active = _get_last_active_time(source)
        most_used = _get_most_used_model(source)

        if process_running and active_sessions > 0:
            status = "running"
        elif process_running:
            status = "idle"
        else:
            status = "offline"

        agents.append(
            {
                "name": name,
                "type": source,
                "status": status,
                "active_sessions": active_sessions,
                "last_active": last_active,
                "model": most_used,
            }
        )

    return agents


def collect_session_detail(session_id: str) -> Optional[dict]:
    """Find and return session detail from any available source."""
    for source in ["kilo", "opencode"]:
        db_path = config.get_db_path(source)
        if not os.path.exists(db_path):
            continue
        detail = _get_session_detail(source, session_id)
        if detail:
            return detail
    return None
