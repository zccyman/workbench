"""Core Assets - SQLite 数据库"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent / "workbench.db"


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_table():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS core_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'general',
            icon TEXT DEFAULT '📦',
            source_url TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            priority INTEGER DEFAULT 0,
            auto_filled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def list_assets() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM core_assets ORDER BY priority DESC, created_at ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_asset(asset_id: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM core_assets WHERE id = ?", (asset_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_asset(name: str, description: str = "", category: str = "general",
              icon: str = "📦", source_url: str = "", tags: list = None,
              priority: int = 0, auto_filled: bool = False) -> dict:
    import json
    conn = _get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        """INSERT INTO core_assets (name, description, category, icon, source_url, tags, priority, auto_filled, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, category, icon, source_url, json.dumps(tags or []),
         priority, 1 if auto_filled else 0, now, now)
    )
    conn.commit()
    asset_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM core_assets WHERE id = ?", (asset_id,)).fetchone()
    conn.close()
    return dict(row)


def update_asset(asset_id: int, **kwargs) -> dict | None:
    if not kwargs:
        return get_asset(asset_id)

    import json
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k == "tags":
            sets.append(f"{k} = ?")
            vals.append(json.dumps(v))
        else:
            sets.append(f"{k} = ?")
            vals.append(v)

    sets.append("updated_at = ?")
    vals.append(datetime.now().isoformat())
    vals.append(asset_id)

    conn = _get_conn()
    conn.execute(f"UPDATE core_assets SET {', '.join(sets)} WHERE id = ?", vals)
    conn.commit()
    row = conn.execute("SELECT * FROM core_assets WHERE id = ?", (asset_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def remove_asset(asset_id: int) -> bool:
    conn = _get_conn()
    cursor = conn.execute("DELETE FROM core_assets WHERE id = ?", (asset_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def reorder_assets(asset_ids: list[int]):
    """按给定顺序重设 priority（列表前面的 priority 最高）"""
    conn = _get_conn()
    for i, aid in enumerate(asset_ids):
        priority = len(asset_ids) - i
        conn.execute(
            "UPDATE core_assets SET priority = ?, updated_at = ? WHERE id = ?",
            (priority, datetime.now().isoformat(), aid),
        )
    conn.commit()
    conn.close()


# 初始化表
init_table()
