import os
from fastapi import APIRouter, Query
from ..config import config
from ..backup import get_backup_meta
from ..models import SourceStatus

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceStatus])
def get_sources():
    results = []
    for platform in config.PLATFORMS:
        source_dir = config.get_source_dir(platform)
        backup_dir = config.get_backup_dir(platform)

        meta = get_backup_meta(platform)
        files = meta.get("files", {})

        backup_total_size = 0
        backup_file_count = 0
        if os.path.exists(backup_dir):
            for root, dirs, files_list in os.walk(backup_dir):
                for f in files_list:
                    fp = os.path.join(root, f)
                    try:
                        backup_total_size += os.path.getsize(fp)
                        backup_file_count += 1
                    except OSError:
                        pass

        results.append(
            SourceStatus(
                platform=platform,
                source_dir=source_dir,
                backup_dir=backup_dir,
                source_exists=os.path.exists(source_dir) if source_dir else False,
                backup_exists=os.path.exists(backup_dir),
                last_backup=meta.get("last_backup"),
                backup_file_count=len(files),
                backup_total_size=backup_total_size,
                source_deleted=meta.get("source_deleted", False),
            )
        )
    return results
