import os
import json
import shutil
import glob as glob_mod
import time
from datetime import datetime
from typing import Optional
from .config import config
from .models import BackupResult, DeleteSourceResult, BackupMeta, BackupHistoryEntry


def _load_meta(platform: str) -> dict:
    meta_path = config.get_meta_path(platform)
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            pass
    return {
        "platform": platform,
        "last_backup": None,
        "last_backup_status": None,
        "total_backups": 0,
        "files": {},
        "history": [],
        "source_deleted": False,
        "last_delete_time": None,
    }


def _save_meta(platform: str, meta: dict):
    backup_dir = config.get_backup_dir(platform)
    os.makedirs(backup_dir, exist_ok=True)
    meta_path = config.get_meta_path(platform)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def _should_exclude(filename: str, platform: str) -> bool:
    patterns = config.SOURCE_PATTERNS.get(platform, {})
    exclude_suffixes = patterns.get("exclude_suffixes", ["-shm", "-wal", "-journal"])
    for suffix in exclude_suffixes:
        if filename.endswith(suffix):
            return True
    return False


def _collect_db_files(platform: str) -> list:
    source_dir = config.get_source_dir(platform)
    if not source_dir or not os.path.exists(source_dir):
        return []

    patterns = config.SOURCE_PATTERNS.get(platform, {})
    collected = []

    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if not filename.endswith(".db") and not filename.endswith(".json"):
                continue
            if _should_exclude(filename, platform):
                continue
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, source_dir)
            collected.append(rel_path)

    return collected


def _find_user_subdirs(platform: str) -> list:
    source_dir = config.get_source_dir(platform)
    if not source_dir or not os.path.exists(source_dir):
        return []

    subdirs = []
    for entry in os.listdir(source_dir):
        full_path = os.path.join(source_dir, entry)
        if os.path.isdir(full_path):
            if entry in ("All Users", "Applet", "WMPF"):
                continue
            subdirs.append(entry)
    return subdirs


def incremental_backup(platform: str) -> BackupResult:
    start_time = time.time()
    source_dir = config.get_source_dir(platform)
    backup_dir = config.get_backup_dir(platform)

    if not source_dir or not os.path.exists(source_dir):
        return BackupResult(
            platform=platform,
            status="error",
            message=f"Source directory not found: {source_dir}",
        )

    os.makedirs(backup_dir, exist_ok=True)
    meta = _load_meta(platform)
    existing_files = meta.get("files", {})

    new_count = 0
    updated_count = 0
    skipped_count = 0
    total_size = 0

    all_source_files = {}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in files:
            if _should_exclude(filename, platform):
                continue
            if (
                not filename.endswith(".db")
                and not filename.endswith(".dat")
                and not filename.endswith(".data")
            ):
                continue

            src_path = os.path.join(root, filename)
            rel_path = os.path.relpath(src_path, source_dir)
            rel_path = rel_path.replace("\\", "/")

            try:
                stat = os.stat(src_path)
            except OSError:
                continue

            all_source_files[rel_path] = {
                "mtime": stat.st_mtime,
                "size": stat.st_size,
            }

            old_info = existing_files.get(rel_path)
            dst_path = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            need_copy = False
            if old_info is None:
                need_copy = True
                new_count += 1
            elif (
                old_info.get("mtime") != stat.st_mtime
                or old_info.get("size") != stat.st_size
            ):
                need_copy = True
                updated_count += 1
            elif not os.path.exists(dst_path):
                need_copy = True
                updated_count += 1
            else:
                skipped_count += 1

            if need_copy:
                try:
                    shutil.copy2(src_path, dst_path)
                    total_size += stat.st_size
                except OSError as e:
                    skipped_count += 1
                    continue

    meta["files"] = all_source_files
    meta["last_backup"] = datetime.now().isoformat()
    meta["last_backup_status"] = "completed"
    meta["total_backups"] = meta.get("total_backups", 0) + 1

    history_entry = {
        "timestamp": meta["last_backup"],
        "platform": platform,
        "status": "completed",
        "new_files": new_count,
        "updated_files": updated_count,
        "skipped_files": skipped_count,
        "total_size": total_size,
    }
    history = meta.get("history", [])
    history.append(history_entry)
    meta["history"] = history

    _save_meta(platform, meta)

    duration_ms = int((time.time() - start_time) * 1000)
    total_files = new_count + updated_count + skipped_count

    return BackupResult(
        platform=platform,
        status="completed",
        total_files=total_files,
        new_files=new_count,
        updated_files=updated_count,
        skipped_files=skipped_count,
        total_size=total_size,
        duration_ms=duration_ms,
        message=f"Backup completed: {new_count} new, {updated_count} updated, {skipped_count} skipped",
    )


def delete_source_data(platform: str) -> DeleteSourceResult:
    source_dir = config.get_source_dir(platform)
    backup_dir = config.get_backup_dir(platform)
    meta = _load_meta(platform)

    if not meta.get("files"):
        return DeleteSourceResult(
            platform=platform,
            status="error",
            errors=["No backup found. Please backup first."],
        )

    if not os.path.exists(backup_dir):
        return DeleteSourceResult(
            platform=platform,
            status="error",
            errors=["Backup directory not found."],
        )

    backup_files = os.listdir(backup_dir)
    if "backup_meta.json" not in backup_files:
        return DeleteSourceResult(
            platform=platform,
            status="error",
            errors=["Backup metadata not found. Backup may be corrupted."],
        )

    deleted_files = 0
    failed_files = 0
    freed_size = 0
    errors = []

    for rel_path, file_info in meta["files"].items():
        src_path = os.path.join(source_dir, rel_path)
        if not os.path.exists(src_path):
            continue

        try:
            file_size = os.path.getsize(src_path)
            os.remove(src_path)
            deleted_files += 1
            freed_size += file_size
        except OSError as e:
            failed_files += 1
            errors.append(f"{rel_path}: {str(e)}")

    meta["source_deleted"] = True
    meta["last_delete_time"] = datetime.now().isoformat()
    _save_meta(platform, meta)

    return DeleteSourceResult(
        platform=platform,
        status="completed",
        deleted_files=deleted_files,
        failed_files=failed_files,
        freed_size=freed_size,
        errors=errors,
    )


def get_backup_meta(platform: str) -> Optional[dict]:
    return _load_meta(platform)


def get_backup_history(platform: Optional[str] = None) -> list:
    if platform:
        platforms = [platform]
    else:
        platforms = config.PLATFORMS

    all_history = []
    for p in platforms:
        meta = _load_meta(p)
        for entry in meta.get("history", []):
            all_history.append(
                BackupHistoryEntry(
                    timestamp=entry.get("timestamp", ""),
                    platform=p,
                    status=entry.get("status", ""),
                    new_files=entry.get("new_files", 0),
                    updated_files=entry.get("updated_files", 0),
                    skipped_files=entry.get("skipped_files", 0),
                    total_size=entry.get("total_size", 0),
                )
            )

    all_history.sort(key=lambda x: x.timestamp, reverse=True)
    return all_history
