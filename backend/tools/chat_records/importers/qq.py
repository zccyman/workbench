import os
from ..config import config
from ..database import db


def import_qq_data(decrypt_key: str = "") -> dict:
    backup_dir = config.get_backup_dir("qq")
    if not os.path.exists(backup_dir):
        return {
            "status": "error",
            "message": "No backup found. Run backup first.",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
        }

    if not decrypt_key:
        return {
            "status": "error",
            "message": "Decryption key required. Set QQ_DB_KEY env var or pass --decrypt-key.",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
        }

    total = 0
    imported = 0
    failed = 0
    errors = []

    try:
        from pysqlcipher3 import dbapi2 as sqlcipher
    except ImportError:
        return {
            "status": "error",
            "message": "pysqlcipher3 not installed.",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": ["pysqlcipher3 not available"],
        }

    msg_dbs = _find_qq_dbs(backup_dir, ["nt_msg.db"])
    group_dbs = _find_qq_dbs(backup_dir, ["group_info.db"])
    profile_dbs = _find_qq_dbs(backup_dir, ["profile_info.db"])

    for db_path in group_dbs:
        total += 1
        try:
            groups = _read_qq_groups(sqlcipher, db_path, decrypt_key)
            for g in groups:
                db.execute_write(
                    """INSERT OR REPLACE INTO chat_contact
                    (id, platform, name, type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    g,
                )
            imported += 1
        except Exception as e:
            failed += 1
            errors.append(f"{db_path}: {str(e)}")

    for db_path in profile_dbs:
        total += 1
        try:
            profiles = _read_qq_profiles(sqlcipher, db_path, decrypt_key)
            for p in profiles:
                db.execute_write(
                    """INSERT OR REPLACE INTO chat_contact
                    (id, platform, name, alias, type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    p,
                )
            imported += 1
        except Exception as e:
            failed += 1
            errors.append(f"{db_path}: {str(e)}")

    for db_path in msg_dbs:
        total += 1
        try:
            messages = _read_qq_messages(sqlcipher, db_path, decrypt_key)
            for m in messages:
                db.execute_write(
                    """INSERT OR REPLACE INTO chat_message
                    (id, platform, conversation_id, sender_id, sender_name, content, msg_type, timestamp, extra_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    m,
                )
            imported += 1
        except Exception as e:
            failed += 1
            errors.append(f"{db_path}: {str(e)}")

    return {
        "status": "completed",
        "total": total,
        "imported": imported,
        "failed": failed,
        "errors": errors,
    }


def _find_qq_dbs(base_dir: str, names: list) -> list:
    found = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(("-shm", "-wal", "-journal")):
                continue
            if f in names:
                found.append(os.path.join(root, f))
    return found


def _read_qq_groups(sqlcipher, db_path: str, key: str) -> list:
    import time

    now = int(time.time() * 1000)
    conn = sqlcipher.connect(db_path)
    conn.execute(f"PRAGMA key = \"x'{key}'\"")
    cursor = conn.execute("SELECT groupCode, groupName FROM group_base_info")
    results = []
    for row in cursor:
        results.append((row[0] or "", "qq", row[1] or "", "group", now, now))
    conn.close()
    return results


def _read_qq_profiles(sqlcipher, db_path: str, key: str) -> list:
    import time

    now = int(time.time() * 1000)
    conn = sqlcipher.connect(db_path)
    conn.execute(f"PRAGMA key = \"x'{key}'\"")
    cursor = conn.execute("SELECT uin, nick, remark FROM buddy_profile_info")
    results = []
    for row in cursor:
        results.append(
            (str(row[0] or ""), "qq", row[1] or "", row[2] or "", "user", now, now)
        )
    conn.close()
    return results


def _read_qq_messages(sqlcipher, db_path: str, key: str) -> list:
    conn = sqlcipher.connect(db_path)
    conn.execute(f"PRAGMA key = \"x'{key}'\"")
    tables_cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in tables_cursor]
    conn.close()
    return []
