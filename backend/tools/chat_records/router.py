from fastapi import APIRouter
from .routes import (
    backup,
    sources,
    contacts,
    conversations,
    messages,
    search,
    stats,
    import_data,
)

router = APIRouter(tags=["chat-records"])

router.include_router(backup.router)
router.include_router(sources.router)
router.include_router(contacts.router)
router.include_router(conversations.router)
router.include_router(messages.router)
router.include_router(search.router)
router.include_router(stats.router)
router.include_router(import_data.router)
