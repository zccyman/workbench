import os
import json
from ..config import config
from ..database import db
from ..routes.import_data import _import_progress


def import_wechat_data(decrypt_key: str = "") -> dict:
    backup_dir = config.get_backup_dir("wechat")
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
            "message": "Decryption key required. Set WECHAT_DB_KEY env var or pass --decrypt-key.",
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
            "message": "pysqlcipher3 not installed. Run: pip install pysqlcipher3",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": ["pysqlcipher3 not available"],
        }

    msg_dbs = _find_db_files(backup_dir, ["ChatMsg.db", "Multi/MSG", "Multi/MediaMSG"])
    contact_dbs = _find_db_files(backup_dir, ["MicroMsg.db"])

    for db_path in contact_dbs:
        total += 1
        try:
            contacts = _read_wechat_contacts(sqlcipher, db_path, decrypt_key)
            for c in contacts:
                db.execute_write(
                    """INSERT OR REPLACE INTO chat_contact
                    (id, platform, name, alias, remark, type, avatar_url, extra_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    c,
                )
            imported += 1
        except Exception as e:
            failed += 1
            errors.append(f"{db_path}: {str(e)}")

    for db_path in msg_dbs:
        total += 1
        try:
            messages = _read_wechat_messages(sqlcipher, db_path, decrypt_key)
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


def import_wechat_data_with_progress(
    decrypt_key: str = "", task_id: str = "", range: str = "all"
) -> dict:
    backup_dir = config.get_backup_dir("wechat")
    if not os.path.exists(backup_dir):
        return {
            "status": "error",
            "message": "No backup found. Run backup first.",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
            "total_messages": 0,
            "processed": 0,
        }

    if not decrypt_key:
        return {
            "status": "error",
            "message": "Decryption key required. Set WECHAT_DB_KEY env var or pass --decrypt-key.",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
            "total_messages": 0,
            "processed": 0,
        }

    import time

    now_ms = int(time.time() * 1000)
    range_ms = {
        "today": 24 * 60 * 60 * 1000,
        "3days": 3 * 24 * 60 * 60 * 1000,
        "week": 7 * 24 * 60 * 60 * 1000,
        "month": 30 * 24 * 60 * 60 * 1000,
    }.get(range, 0)

    min_timestamp = now_ms - range_ms if range_ms > 0 else 0

    try:
        from pysqlcipher3 import dbapi2 as sqlcipher
    except ImportError:
        return {
            "status": "error",
            "message": "pysqlcipher3 not installed. Run: pip install pysqlcipher3",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": ["pysqlcipher3 not available"],
            "total_messages": 0,
            "processed": 0,
        }

    msg_dbs = _find_db_files(backup_dir, ["ChatMsg.db", "Multi/MSG", "Multi/MediaMSG"])
    contact_dbs = _find_db_files(backup_dir, ["MicroMsg.db"])

    total = len(contact_dbs) + len(msg_dbs)
    imported = 0
    failed = 0
    errors = []
    processed = 0
    total_messages = 0
    conversation_counts = {}

    for db_path in contact_dbs:
        if task_id and task_id in _import_progress:
            _import_progress[task_id].current_file = db_path
        try:
            contacts = _read_wechat_contacts(sqlcipher, db_path, decrypt_key)
            for c in contacts:
                db.execute_write(
                    """INSERT OR REPLACE INTO chat_contact
                    (id, platform, name, alias, remark, type, avatar_url, extra_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    c,
                )
            imported += 1
            processed += 1
            if task_id and task_id in _import_progress:
                _import_progress[task_id].processed = processed
                _import_progress[task_id].total = total
        except Exception as e:
            failed += 1
            errors.append(f"{db_path}: {str(e)}")

    for db_path in msg_dbs:
        if task_id and task_id in _import_progress:
            _import_progress[task_id].current_file = db_path
        try:
            messages = _read_wechat_messages(
                sqlcipher, db_path, decrypt_key, min_timestamp
            )
            msg_count = len(messages)
            total_messages += msg_count
            for m in messages:
                conv_id = m[2]
                conversation_counts[conv_id] = conversation_counts.get(conv_id, 0) + 1
                db.execute_write(
                    """INSERT OR REPLACE INTO chat_message
                    (id, platform, conversation_id, sender_id, sender_name, content, msg_type, timestamp, extra_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    m,
                )
            imported += 1
            processed += 1
            if task_id and task_id in _import_progress:
                _import_progress[task_id].processed = processed
                _import_progress[task_id].total = total
                _import_progress[task_id].total_messages = total_messages
        except Exception as e:
            failed += 1
            errors.append(f"{db_path}: {str(e)}")

    imported_conversations = [
        {"name": conv_id, "count": cnt} for conv_id, cnt in conversation_counts.items()
    ]

    return {
        "status": "completed",
        "total": total,
        "imported": imported,
        "failed": failed,
        "errors": errors,
        "total_messages": total_messages,
        "processed": processed,
        "imported_conversations": imported_conversations,
    }


def _find_db_files(base_dir: str, prefixes: list) -> list:
    found = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(("-shm", "-wal", "-journal")):
                continue
            if not f.endswith(".db"):
                continue
            for prefix in prefixes:
                if prefix in os.path.join(root, f).replace("\\", "/"):
                    found.append(os.path.join(root, f))
                    break
    return found


def _read_wechat_contacts(sqlcipher, db_path: str, key: str) -> list:
    conn = sqlcipher.connect(db_path)
    conn.execute(f"PRAGMA key = \"x'{key}'\"")
    conn.execute("PRAGMA cipher_page_size = 4096")
    conn.execute("PRAGMA kdf_iter = 64000")
    cursor = conn.execute(
        "SELECT userName, alias, nickName, dbContactRemark, type FROM Contact"
    )
    results = []
    import time

    now = int(time.time() * 1000)
    for row in cursor:
        results.append(
            (
                row[0] or "",
                "wechat",
                row[2] or "",
                row[1] or "",
                row[3] or "",
                "user",
                None,
                None,
                now,
                now,
            )
        )
    conn.close()
    return results


def _read_wechat_messages(
    sqlcipher, db_path: str, key: str, min_timestamp: int = 0
) -> list:
    conn = sqlcipher.connect(db_path)
    conn.execute(f"PRAGMA key = \"x'{key}'\"")
    conn.execute("PRAGMA cipher_page_size = 4096")
    conn.execute("PRAGMA kdf_iter = 64000")

    if min_timestamp > 0:
        cursor = conn.execute(
            f"SELECT localId, talker, type, createTime, content, msgSvrId FROM MSG WHERE createTime >= {min_timestamp}"
        )
    else:
        cursor = conn.execute(
            "SELECT localId, talker, type, createTime, content, msgSvrId FROM MSG"
        )
    results = []
    for row in cursor:
        msg_type = _wechat_msg_type(row[2])
        results.append(
            (
                str(row[5] or row[0]),
                "wechat",
                row[1] or "",
                None,
                None,
                row[4] or "",
                msg_type,
                row[3] or 0,
                None,
            )
        )
    conn.close()
    return results


def _wechat_msg_type(type_code: int) -> str:
    mapping = {
        1: "text",
        3: "image",
        34: "voice",
        43: "video",
        47: "emoji",
        49: "link",
        10000: "system",
        10002: "system",
    }
    return mapping.get(type_code, "text")
