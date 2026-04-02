from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from ..services.export_service import (
    export_session_markdown,
    export_batch_markdown,
    export_session_json,
    export_all_to_directory,
)

router = APIRouter(prefix="/export", tags=["export"])

# In-memory progress tracking
_export_progress = {}


class ExportToDirRequest(BaseModel):
    output_dir: str
    source: str = "kilo"


class ExportToDirResponse(BaseModel):
    task_id: str
    total: int
    message: str


class ExportProgressResponse(BaseModel):
    task_id: str
    status: str  # "running" | "completed" | "failed"
    total: int
    exported: int
    failed: int
    output_dir: Optional[str] = None
    errors: List[str] = []


@router.get("/markdown/{session_id}", response_class=PlainTextResponse)
def export_markdown(
    session_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    md = export_session_markdown(session_id, source)
    if not md:
        raise HTTPException(status_code=404, detail="Session not found")
    return md


@router.get("/json/{session_id}")
def export_json(
    session_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    data = export_session_json(session_id, source)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    return data


@router.post("/to-directory", response_model=ExportToDirResponse)
def export_to_directory(request: ExportToDirRequest, background_tasks: BackgroundTasks):
    """Start batch export of all sessions to a directory. Runs in background."""
    import uuid
    task_id = str(uuid.uuid4())[:8]
    _export_progress[task_id] = {
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
            result = export_all_to_directory(request.source, request.output_dir)
            _export_progress[task_id].update({
                "status": "completed",
                "total": result["total"],
                "exported": result["exported"],
                "failed": result["failed"],
                "output_dir": result["output_dir"],
                "errors": result.get("errors", []),
            })
        except Exception as e:
            _export_progress[task_id].update({
                "status": "failed",
                "errors": [str(e)],
            })

    background_tasks.add_task(_run_export)
    return ExportToDirResponse(task_id=task_id, total=0, message="Export started in background")


@router.get("/to-directory/progress/{task_id}", response_model=ExportProgressResponse)
def get_export_progress(task_id: str):
    """Get progress of a batch export task."""
    if task_id not in _export_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return ExportProgressResponse(**_export_progress[task_id])
