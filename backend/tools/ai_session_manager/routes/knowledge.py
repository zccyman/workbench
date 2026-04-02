from fastapi import APIRouter, Query
from .services.knowledge_service import extract_knowledge
from .models import KnowledgeExtraction

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/extract", response_model=KnowledgeExtraction)
def extract_session_knowledge(
    session_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    return extract_knowledge(session_id, source)


@router.get("/session/{session_id}", response_model=KnowledgeExtraction)
def get_session_knowledge(
    session_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    return extract_knowledge(session_id, source)
