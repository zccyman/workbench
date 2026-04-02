from fastapi import APIRouter

from .routes import (
    sessions,
    messages,
    projects,
    search,
    stats,
    knowledge,
    export,
    sources,
    tab_contents,
)

router = APIRouter(tags=["ai-session-manager"])

router.include_router(sessions.router)
router.include_router(messages.router)
router.include_router(projects.router)
router.include_router(search.router)
router.include_router(stats.router)
router.include_router(knowledge.router)
router.include_router(export.router)
router.include_router(sources.router)
router.include_router(tab_contents.router)
