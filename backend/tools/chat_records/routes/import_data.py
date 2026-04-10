from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from typing import Optional
from ..models import ImportRequest, ImportProgress
from ..config import config
from ..database import db

router = APIRouter(prefix="/import", tags=["import"])

_import_progress = {}
_import_global_progress = {}


@router.post("/{platform}")
def start_import(
    platform: str,
    background_tasks: BackgroundTasks,
    decrypt_key: Optional[str] = Query(None),
    range: Optional[str] = Query("all"),
):
    if platform not in config.PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    import uuid

    task_id = str(uuid.uuid4())[:8]
    _import_progress[task_id] = ImportProgress(
        task_id=task_id,
        status="pending",
        platform=platform,
    )

    def _run():
        _import_progress[task_id].status = "running"
        try:
            if platform == "wechat":
                from ..importers.wechat import import_wechat_data_with_progress

                result = import_wechat_data_with_progress(
                    decrypt_key or config.WECHAT_DB_KEY, task_id, range
                )
            elif platform == "qq":
                from ..importers.qq import import_qq_data_with_progress

                result = import_qq_data_with_progress(
                    decrypt_key or config.QQ_DB_KEY, task_id, range
                )
            elif platform == "qq":
                from ..importers.qq import import_qq_data_with_progress

                result = import_qq_data_with_progress(
                    decrypt_key or config.QQ_DB_KEY, task_id
                )
            elif platform == "feishu":
                from ..importers.feishu import import_feishu_data

                result = import_feishu_data(
                    config.FEISHU_APP_ID, config.FEISHU_APP_SECRET
                )
            else:
                result = {
                    "status": "error",
                    "message": f"Unsupported platform: {platform}",
                }

            _import_progress[task_id].status = result.get("status", "completed")
            _import_progress[task_id].total = result.get("total", 0)
            _import_progress[task_id].imported = result.get("imported", 0)
            _import_progress[task_id].failed = result.get("failed", 0)
            _import_progress[task_id].errors = result.get("errors", [])
            _import_progress[task_id].result = result
            _import_progress[task_id].total_messages = result.get("total_messages", 0)
            _import_progress[task_id].processed = result.get("processed", 0)
        except Exception as e:
            _import_progress[task_id].status = "failed"
            _import_progress[task_id].errors = [str(e)]
            _import_progress[task_id].result = {"message": str(e)}

    background_tasks.add_task(_run)
    return {"task_id": task_id, "status": "started", "platform": platform}


@router.get("/status/{task_id}", response_model=ImportProgress)
def get_import_status(task_id: str):
    if task_id not in _import_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return _import_progress[task_id]
