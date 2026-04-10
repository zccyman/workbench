from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from typing import Optional
from datetime import datetime
import os
import shutil
from ..models import (
    BackupResult,
    DeleteSourceResult,
    DeleteSourceRequest,
    BackupHistoryEntry,
)
from ..backup import incremental_backup, delete_source_data, get_backup_history
from ..config import config

router = APIRouter(prefix="/backup", tags=["backup"])

_backup_progress = {}


def _run_backup_with_progress(task_id: str, platform: str, full: bool = False):
    from .. import backup as backup_module

    try:
        source_dir = config.get_source_dir(platform)
        backup_dir = config.get_backup_dir(platform)
        os.makedirs(backup_dir, exist_ok=True)

        meta = backup_module._load_meta(platform)

        if full:
            existing_files = {}
        else:
            existing_files = meta.get("files", {})

        all_source_files = {}
        all_files = []

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                if backup_module._should_exclude(filename, platform):
                    continue
                if (
                    not filename.endswith(".db")
                    and not filename.endswith(".dat")
                    and not filename.endswith(".data")
                ):
                    continue
                src_path = os.path.join(root, filename)
                rel_path = os.path.relpath(src_path, source_dir).replace("\\", "/")
                try:
                    stat = os.stat(src_path)
                    all_files.append(
                        {"path": rel_path, "mtime": stat.st_mtime, "size": stat.st_size}
                    )
                    all_source_files[rel_path] = {
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                    }
                except OSError:
                    continue

        total_files = len(all_files)
        _backup_progress[task_id]["total_files"] = total_files

        new_count = 0
        updated_count = 0
        skipped_count = 0
        total_size = 0

        for i, f in enumerate(all_files):
            rel_path = f["path"]
            src_path = os.path.join(source_dir, rel_path)
            dst_path = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            old_info = existing_files.get(rel_path)
            need_copy = False
            if old_info is None:
                need_copy = True
                new_count += 1
            elif (
                old_info.get("mtime") != f["mtime"] or old_info.get("size") != f["size"]
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
                    total_size += f["size"]
                except OSError:
                    skipped_count += 1

            _backup_progress[task_id].update(
                {
                    "processed": i + 1,
                    "current_file": rel_path,
                    "new_count": new_count,
                    "updated_count": updated_count,
                    "skipped_count": skipped_count,
                    "copied_size": total_size,
                }
            )

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
        meta["history"] = meta.get("history", []) + [history_entry]
        backup_module._save_meta(platform, meta)

        _backup_progress[task_id].update(
            {
                "status": "completed",
                "result": {
                    "platform": platform,
                    "status": "completed",
                    "total_files": new_count + updated_count + skipped_count,
                    "new_files": new_count,
                    "updated_files": updated_count,
                    "skipped_files": skipped_count,
                    "total_size": total_size,
                    "message": f"Backup completed: {new_count} new, {updated_count} updated, {skipped_count} skipped",
                },
            }
        )
    except Exception as e:
        _backup_progress[task_id].update(
            {
                "status": "failed",
                "result": {"platform": platform, "status": "error", "message": str(e)},
            }
        )


@router.post("/{platform}", response_model=BackupResult)
def start_backup(
    platform: str,
    background_tasks: BackgroundTasks,
    full: bool = False,
):
    if platform not in config.PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    source_dir = config.get_source_dir(platform)
    if not source_dir or not import_os_path_exists(source_dir):
        raise HTTPException(
            status_code=404, detail=f"Source directory not found: {source_dir}"
        )

    import uuid

    task_id = str(uuid.uuid4())[:8]
    _backup_progress[task_id] = {
        "task_id": task_id,
        "platform": platform,
        "status": "running",
        "result": None,
        "processed": 0,
        "total_files": 0,
        "current_file": "",
        "new_count": 0,
        "updated_count": 0,
        "skipped_count": 0,
        "copied_size": 0,
    }

    background_tasks.add_task(_run_backup_with_progress, task_id, platform, full)
    return BackupResult(
        platform=platform,
        status="running",
        message=f"Backup started with task_id: {task_id}, full: {full}",
    )


@router.get("/status/{task_id}")
def get_backup_status(task_id: str):
    if task_id not in _backup_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return _backup_progress[task_id]


@router.get("/history", response_model=list[BackupHistoryEntry])
def history(platform: Optional[str] = Query(None)):
    return get_backup_history(platform)


@router.post("/{platform}/execute", response_model=BackupResult)
def execute_backup_sync(platform: str):
    if platform not in config.PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    source_dir = config.get_source_dir(platform)
    if not source_dir or not import_os_path_exists(source_dir):
        raise HTTPException(
            status_code=404, detail=f"Source directory not found: {source_dir}"
        )

    return incremental_backup(platform)


@router.post("/{platform}/delete-source", response_model=DeleteSourceResult)
def delete_source(platform: str, request: DeleteSourceRequest):
    if platform not in config.PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    if request.confirm_name != platform:
        raise HTTPException(
            status_code=400,
            detail=f"Confirmation name mismatch. Expected '{platform}', got '{request.confirm_name}'",
        )

    source_dir = config.get_source_dir(platform)
    if not source_dir:
        raise HTTPException(status_code=400, detail="Source directory not configured")

    return delete_source_data(platform)


def import_os_path_exists(path: str) -> bool:
    import os

    return os.path.exists(path)
