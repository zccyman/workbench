from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
import json
import time
import uuid
import os
import re
from datetime import datetime

from .database import get_db
from .models import (
    TabContent,
    TabContentCreate,
    TabContentWithStats,
    TabContentMessage,
    timestamp_to_str,
)

router = APIRouter(prefix="/tab-contents", tags=["tab-contents"])

# In-memory progress tracking for tab content exports
_tab_export_progress = {}


def get_app_db():
    """Get the app's own database for storing tab contents."""
    from .database import Database
    import os

    db_path = os.environ.get("APP_DB_PATH", "data/app.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = Database(db_path)
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS tab_contents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT,
            markdown TEXT NOT NULL,
            messages TEXT,
            source TEXT DEFAULT 'tabbit',
            created_at INTEGER,
            updated_at INTEGER
        )
    """)
    return db


@router.post("", response_model=TabContent)
def create_tab_content(content: TabContentCreate):
    db = get_app_db()
    content_id = f"tab_{uuid.uuid4().hex[:12]}"
    now = int(time.time() * 1000)
    messages_json = json.dumps([m.model_dump() for m in content.messages])

    db.execute_write(
        """INSERT INTO tab_contents (id, title, url, markdown, messages, source, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            content_id,
            content.title,
            content.url,
            content.markdown,
            messages_json,
            content.source,
            now,
            now,
        ),
    )

    return TabContent(
        id=content_id,
        title=content.title,
        url=content.url,
        markdown=content.markdown,
        messages=content.messages,
        source=content.source,
        created_at=now,
        updated_at=now,
    )

    return TabContent(
        id=content_id,
        title=content.title,
        url=content.url,
        markdown=content.markdown,
        messages=content.messages,
        source=content.source,
        created_at=now,
        updated_at=now,
    )


@router.get("", response_model=List[TabContentWithStats])
def list_tab_contents(
    source: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    db = get_app_db()

    query = "SELECT id, title, url, markdown, messages, source, created_at, updated_at FROM tab_contents"
    params = []

    if source:
        query += " WHERE source = ?"
        params.append(source)

    query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))

    contents = []
    for row in rows:
        messages = []
        if row[4]:
            try:
                messages = [TabContentMessage(**m) for m in json.loads(row[4])]
            except:
                messages = []

        contents.append(
            TabContentWithStats(
                id=row[0],
                title=row[1],
                url=row[2],
                markdown=row[3],
                messages=messages,
                source=row[5] or "tabbit",
                created_at=row[6],
                updated_at=row[7],
                message_count=len(messages),
                char_count=len(row[3]) if row[3] else 0,
                created_at_str=timestamp_to_str(row[6]) if row[6] else None,
                updated_at_str=timestamp_to_str(row[7]) if row[7] else None,
            )
        )

    return contents


@router.get("/search", response_model=List[TabContentWithStats])
def search_tab_contents(
    q: str = Query(..., min_length=1), limit: int = Query(50, ge=1, le=500)
):
    db = get_app_db()
    search_term = f"%{q}%"

    query = """
        SELECT id, title, url, markdown, messages, source, created_at, updated_at
        FROM tab_contents
        WHERE title LIKE ? OR markdown LIKE ?
        ORDER BY updated_at DESC
        LIMIT ?
    """

    rows = db.execute_query(query, (search_term, search_term, limit))

    contents = []
    for row in rows:
        messages = []
        if row[4]:
            try:
                messages = [TabContentMessage(**m) for m in json.loads(row[4])]
            except:
                messages = []

        contents.append(
            TabContentWithStats(
                id=row[0],
                title=row[1],
                url=row[2],
                markdown=row[3],
                messages=messages,
                source=row[5] or "tabbit",
                created_at=row[6],
                updated_at=row[7],
                message_count=len(messages),
                char_count=len(row[3]) if row[3] else 0,
                created_at_str=timestamp_to_str(row[6]) if row[6] else None,
                updated_at_str=timestamp_to_str(row[7]) if row[7] else None,
            )
        )

    return contents


@router.get("/{content_id}", response_model=TabContentWithStats)
def get_tab_content(content_id: str):
    db = get_app_db()

    row = db.execute_query_one(
        "SELECT id, title, url, markdown, messages, source, created_at, updated_at FROM tab_contents WHERE id = ?",
        (content_id,),
    )

    if not row:
        raise HTTPException(status_code=404, detail="Tab content not found")

    messages = []
    if row[4]:
        try:
            messages = [TabContentMessage(**m) for m in json.loads(row[4])]
        except:
            messages = []

    return TabContentWithStats(
        id=row[0],
        title=row[1],
        url=row[2],
        markdown=row[3],
        messages=messages,
        source=row[5] or "tabbit",
        created_at=row[6],
        updated_at=row[7],
        message_count=len(messages),
        char_count=len(row[3]) if row[3] else 0,
        created_at_str=timestamp_to_str(row[6]) if row[6] else None,
        updated_at_str=timestamp_to_str(row[7]) if row[7] else None,
    )


@router.put("/{content_id}", response_model=TabContent)
def update_tab_content(content_id: str, content: TabContentCreate):
    db = get_app_db()
    now = int(time.time() * 1000)
    messages_json = json.dumps([m.model_dump() for m in content.messages])

    existing = db.execute_query_one(
        "SELECT id FROM tab_contents WHERE id = ?", (content_id,)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Tab content not found")

    db.execute_write(
        """UPDATE tab_contents SET title=?, url=?, markdown=?, messages=?, source=?, updated_at=?
           WHERE id=?""",
        (
            content.title,
            content.url,
            content.markdown,
            messages_json,
            content.source,
            now,
            content_id,
        ),
    )

    return TabContent(
        id=content_id,
        title=content.title,
        url=content.url,
        markdown=content.markdown,
        messages=content.messages,
        source=content.source,
        created_at=existing[6] if len(existing) > 6 else now,
        updated_at=now,
    )


@router.delete("/{content_id}")
def delete_tab_content(content_id: str):
    db = get_app_db()

    existing = db.execute_query_one(
        "SELECT id FROM tab_contents WHERE id = ?", (content_id,)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Tab content not found")

    db.execute_write("DELETE FROM tab_contents WHERE id = ?", (content_id,))

    return {"message": "Deleted successfully"}


@router.get("/{content_id}/markdown")
def export_markdown(content_id: str):
    db = get_app_db()

    row = db.execute_query_one(
        "SELECT title, markdown FROM tab_contents WHERE id = ?", (content_id,)
    )

    if not row:
        raise HTTPException(status_code=404, detail="Tab content not found")

    return {"title": row[0], "markdown": row[1]}


def _sanitize_filename(name: str, max_len: int = 80) -> str:
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', "", name)
    name = re.sub(r"\s+", "-", name)
    name = name.strip("-.")
    return name[:max_len] if name else "untitled"


def _convert_windows_path(path: str) -> str:
    """Convert Windows path to WSL path if needed."""
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", path)
    if m:
        return f"/mnt/{m.group(1).lower()}/{m.group(2).replace('\\', '/')}"
    return path


class TabExportRequest(BaseModel):
    output_dir: str
    source: Optional[str] = None


class TabExportProgress(BaseModel):
    task_id: str
    status: str
    total: int
    exported: int
    failed: int
    output_dir: Optional[str] = None
    errors: List[str] = []


@router.post("/export-to-directory")
def export_tab_contents_to_directory(
    request: TabExportRequest, background_tasks: BackgroundTasks
):
    """Export all tab contents as markdown files to a directory."""
    task_id = str(uuid.uuid4())[:8]
    _tab_export_progress[task_id] = {
        "task_id": task_id,
        "status": "running",
        "total": 0,
        "exported": 0,
        "failed": 0,
        "output_dir": request.output_dir,
        "errors": [],
    }

    def _run_export():
        try:
            output_dir = _convert_windows_path(request.output_dir)
            os.makedirs(output_dir, exist_ok=True)

            db = get_app_db()
            query = "SELECT id, title, url, markdown, messages, source, created_at, updated_at FROM tab_contents"
            params = []
            if request.source:
                query += " WHERE source = ?"
                params.append(request.source)
            query += " ORDER BY updated_at DESC"

            rows = db.execute_query(query, tuple(params) if params else ())
            total = len(rows)

            if total == 0:
                _tab_export_progress[task_id].update(
                    {
                        "status": "completed",
                        "total": 0,
                        "exported": 0,
                        "failed": 0,
                        "output_dir": output_dir,
                        "errors": [],
                    }
                )
                return

            exported = 0
            failed = 0
            errors = []

            for i, row in enumerate(rows):
                (
                    content_id,
                    title,
                    url,
                    markdown,
                    messages_json,
                    source,
                    created_at,
                    updated_at,
                ) = row

                if not markdown:
                    failed += 1
                    errors.append(f"Tab {content_id}: no content")
                    continue

                try:
                    # Build markdown with metadata header
                    md_lines = [f"# {title or 'Untitled'}\n"]
                    if url:
                        md_lines.append(f"**URL:** {url}\n")
                    if source:
                        md_lines.append(f"**Source:** {source}\n")
                    if created_at:
                        try:
                            created_str = datetime.fromtimestamp(
                                created_at / 1000
                            ).strftime("%Y-%m-%d %H:%M")
                            md_lines.append(f"**Created:** {created_str}\n")
                        except Exception:
                            pass
                    md_lines.append(f"\n---\n\n{markdown}")

                    safe_title = _sanitize_filename(title or f"tab-{i + 1}")
                    timestamp = ""
                    if updated_at:
                        try:
                            ts = datetime.fromtimestamp(updated_at / 1000)
                            timestamp = ts.strftime("%Y%m%d-%H%M") + "-"
                        except Exception:
                            pass
                    filename = f"{str(i + 1).zfill(6)}-{timestamp}{safe_title}.md"

                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write("\n".join(md_lines))

                    exported += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"Tab {content_id}: {str(e)}")

            _tab_export_progress[task_id].update(
                {
                    "status": "completed",
                    "total": total,
                    "exported": exported,
                    "failed": failed,
                    "output_dir": output_dir,
                    "errors": errors[:10],
                }
            )
        except Exception as e:
            _tab_export_progress[task_id].update(
                {
                    "status": "failed",
                    "errors": [str(e)],
                }
            )

    background_tasks.add_task(_run_export)
    return {"task_id": task_id, "message": "Export started in background"}


@router.get("/export-to-directory/progress/{task_id}")
def get_tab_export_progress(task_id: str):
    """Get progress of a tab content batch export task."""
    if task_id not in _tab_export_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tab_export_progress[task_id]
