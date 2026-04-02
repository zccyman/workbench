import os
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from ..database import get_db


def _sanitize_filename(name: str, max_len: int = 80) -> str:
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', "", name)
    name = re.sub(r"\s+", "-", name)
    name = name.strip("-.")
    return name[:max_len] if name else "untitled"


def _get_session_markdown(session_id: str, source: str) -> Optional[str]:
    """Generate markdown content for a single session."""
    db = get_db(source)

    session = db.execute_query_one(
        "SELECT s.id, s.title, s.time_created, s.time_updated, p.name as project_name, p.worktree "
        "FROM session s LEFT JOIN project p ON s.project_id = p.id WHERE s.id = ?",
        (session_id,),
    )
    if not session:
        return None

    title = session[1] or "Untitled Session"
    time_created = session[2]
    time_updated = session[3]
    project_name = session[4]
    project_dir = session[5]

    if not project_name and project_dir:
        project_name = project_dir.rstrip("/").split("/")[-1]

    # Get messages
    messages = db.execute_query(
        "SELECT id, data FROM message WHERE session_id = ? ORDER BY id ASC",
        (session_id,),
    )

    # Try to get parts (table name may be 'part' or 'message_part')
    parts_data = {}
    if messages:
        msg_ids = [str(m[0]) for m in messages]
        if msg_ids:
            placeholders = ",".join(["?"] * len(msg_ids))
            for table_name in ["part", "message_part"]:
                try:
                    parts = db.execute_query(
                        f"SELECT message_id, data FROM {table_name} WHERE message_id IN ({placeholders}) ORDER BY id ASC",
                        tuple(msg_ids),
                    )
                    for p in parts:
                        mid = str(p[0])
                        if mid not in parts_data:
                            parts_data[mid] = []
                        parts_data[mid].append(p[1])
                    break  # Found the right table
                except Exception:
                    continue  # Try next table name

    # Build markdown
    created_str = (
        datetime.fromtimestamp(time_created / 1000).strftime("%Y-%m-%d %H:%M")
        if time_created
        else "Unknown"
    )

    md = f"# {title}\n\n"
    if project_name:
        md += f"**Project:** {project_name}\n\n"
    md += f"**Time:** {created_str}\n\n"

    msg_count = 0
    for msg in messages:
        msg_id, data_raw = msg[0], msg[1]

        content = ""
        parsed = None
        if data_raw:
            try:
                parsed = json.loads(data_raw) if isinstance(data_raw, str) else data_raw
            except Exception:
                pass

        role = "assistant"
        if parsed:
            role = parsed.get("role", "assistant")
            c = parsed.get("content", "")
            if isinstance(c, str) and c:
                content = c
            elif isinstance(c, list):
                content = "\n".join(
                    item.get("text", "")
                    for item in c
                    if isinstance(item, dict) and item.get("text")
                )

        # Fallback to parts
        if not content:
            p_list = parts_data.get(str(msg_id), [])
            for p_raw in p_list:
                try:
                    p = json.loads(p_raw) if isinstance(p_raw, str) else p_raw
                    if isinstance(p, dict):
                        t = p.get("text", "")
                        if t:
                            content = t
                            break
                except Exception:
                    pass

        if not content:
            continue

        msg_count += 1
        role_label = "👤 User" if role == "user" else "🤖 AI"
        md += f"## {role_label}\n\n{content}\n\n"

    if msg_count == 0:
        return None  # Skip sessions with no extractable content

    md = md.replace(
        f"**Time:** {created_str}\n\n",
        f"**Time:** {created_str}\n**Messages:** {msg_count}\n\n",
    )
    return md


def export_session_markdown(session_id: str, source: str = "kilo") -> str:
    return _get_session_markdown(session_id, source) or ""


def export_batch_markdown(session_ids: List[str], source: str = "kilo") -> List[Dict]:
    results = []
    for sid in session_ids:
        md = _get_session_markdown(sid, source)
        if md:
            results.append({"id": sid, "markdown": md})
    return results


def export_session_json(session_id: str, source: str = "kilo") -> Dict:
    db = get_db(source)
    session = db.execute_query_one(
        "SELECT id, project_id, title, directory, time_created, time_updated FROM session WHERE id = ?",
        (session_id,),
    )
    if not session:
        return {}
    messages = db.execute_query(
        "SELECT id, time_created, data FROM message WHERE session_id = ? ORDER BY time_created ASC",
        (session_id,),
    )
    msg_list = []
    for row in messages:
        try:
            parsed = json.loads(row[2]) if isinstance(row[2], str) else row[2]
            msg_list.append({"id": row[0], "time_created": row[1], "data": parsed})
        except Exception:
            msg_list.append({"id": row[0], "time_created": row[1], "data": row[2]})
    return {
        "session": {
            "id": session[0],
            "title": session[2],
            "directory": session[3],
            "time_created": session[4],
            "time_updated": session[5],
        },
        "messages": msg_list,
    }


def _convert_windows_path(path: str) -> str:
    """Convert Windows path to WSL path if needed."""
    import re

    # G:\path → /mnt/g/path
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", path)
    if m:
        return f"/mnt/{m.group(1).lower()}/{m.group(2).replace('\\', '/')}"
    return path


def export_all_to_directory(source: str, output_dir: str) -> Dict:
    """Export all sessions as .md files to a directory."""
    # Convert Windows path to WSL path
    output_dir = _convert_windows_path(output_dir)

    db = get_db(source)

    sessions = db.execute_query(
        "SELECT s.id, s.title, s.time_created, p.name as project_name, p.worktree "
        "FROM session s LEFT JOIN project p ON s.project_id = p.id "
        "ORDER BY s.time_updated DESC"
    )

    total = len(sessions)
    if total == 0:
        return {
            "total": 0,
            "exported": 0,
            "failed": 0,
            "output_dir": output_dir,
            "errors": [],
        }

    os.makedirs(output_dir, exist_ok=True)

    exported = 0
    failed = 0
    errors = []

    for i, sess in enumerate(sessions):
        sid, title, time_created, project_name, worktree = sess

        if not project_name and worktree:
            project_name = worktree.rstrip("/").split("/")[-1]

        try:
            md = _get_session_markdown(sid, source)
            if not md:
                failed += 1
                errors.append(f"Session {sid}: no content")
                continue

            safe_title = _sanitize_filename(title or f"session-{i + 1}")
            timestamp = ""
            if time_created:
                ts = datetime.fromtimestamp(time_created / 1000)
                timestamp = ts.strftime("%Y%m%d-%H%M") + "-"
            filename = f"{str(i + 1).zfill(6)}-{timestamp}{safe_title}.md"

            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)

            exported += 1
        except Exception as e:
            failed += 1
            errors.append(f"Session {sid}: {str(e)}")

    return {
        "total": total,
        "exported": exported,
        "failed": failed,
        "output_dir": output_dir,
        "errors": errors[:10],
    }
