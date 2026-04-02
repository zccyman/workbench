from fastapi import APIRouter
from ..config import config

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("")
def get_sources():
    return {
        "available": config.get_available_sources(),
        "default": "kilo",
        "paths": {
            "kilo": config.KILO_CODE_DB_PATH,
            "opencode": config.OPENCODE_DB_PATH,
        },
    }


@router.get("/available")
def get_available_sources():
    return config.get_available_sources()
