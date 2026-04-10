"""Skills Manager - 数据库状态持久化"""

import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "workbench.db")


def _get_conn():
    """获取 SQLite 原生连接（skills_manager 用独立连接，不干扰 SQLAlchemy）"""
    import sqlite3

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_table():
    """初始化 skill_status 表"""
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS skill_status (
            skill_id TEXT PRIMARY KEY,
            enabled INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def get_enabled_map() -> dict[str, bool]:
    """获取所有技能的启用状态映射 {skill_id: enabled}"""
    init_table()
    conn = _get_conn()
    rows = conn.execute("SELECT skill_id, enabled FROM skill_status").fetchall()
    conn.close()
    return {row["skill_id"]: bool(row["enabled"]) for row in rows}


def toggle_skill(skill_id: str) -> bool:
    """切换技能启用/禁用状态，返回新状态"""
    init_table()
    conn = _get_conn()

    row = conn.execute(
        "SELECT enabled FROM skill_status WHERE skill_id = ?", (skill_id,)
    ).fetchone()

    if row is None:
        new_state = False  # 默认启用，切换为禁用
    else:
        new_state = not bool(row["enabled"])

    now = datetime.now().isoformat()
    conn.execute(
        """
        INSERT INTO skill_status (skill_id, enabled, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(skill_id) DO UPDATE SET enabled = ?, updated_at = ?
    """,
        (skill_id, int(new_state), now, int(new_state), now),
    )
    conn.commit()
    conn.close()
    return new_state


def set_skill_status(skill_id: str, enabled: bool):
    """设置技能启用/禁用状态"""
    init_table()
    conn = _get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        """
        INSERT INTO skill_status (skill_id, enabled, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(skill_id) DO UPDATE SET enabled = ?, updated_at = ?
    """,
        (skill_id, int(enabled), now, int(enabled), now),
    )
    conn.commit()
    conn.close()
