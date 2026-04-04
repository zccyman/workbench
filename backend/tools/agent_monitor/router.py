import os
from fastapi import APIRouter, Query

from .models import (
    OverviewResponse,
    SessionListResponse,
    SessionItem,
    SessionDetailResponse,
    AgentListResponse,
    AgentStatusItem,
    TrendResponse,
    TrendDataPoint,
    ModelBreakdownResponse,
    ModelBreakdownItem,
    HealthResponse,
    HealthSourceStatus,
)
from .collector import (
    collect_all_data,
    collect_agent_status,
    collect_session_detail,
)
from .analyzer import (
    compute_overview,
    aggregate_trend,
    aggregate_cost_trend,
    compute_model_breakdown,
)

router = APIRouter(tags=["agent-monitor"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    sources = HealthSourceStatus()
    from ..ai_session_manager.config import config

    if os.path.exists(config.KILO_CODE_DB_PATH):
        sources.ai_session_manager = "connected"
        sources.database = "connected"
    try:
        from ..usage_monitor.collector import _get_default_agent_dir

        agent_dir = _get_default_agent_dir()
        if os.path.exists(agent_dir):
            sources.usage_monitor = "connected"
    except ImportError:
        pass

    all_ok = (
        sources.ai_session_manager == "connected" and sources.database == "connected"
    )
    return HealthResponse(status="healthy" if all_ok else "degraded", sources=sources)


@router.get("/overview", response_model=OverviewResponse)
def get_overview():
    data = collect_all_data(limit=500)
    return OverviewResponse(**compute_overview(data["sessions"]))


@router.get("/sessions", response_model=SessionListResponse)
def get_sessions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    agent: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
):
    df = date_from or None
    dt = date_to or None
    data = collect_all_data(date_from=df, date_to=dt, limit=limit, offset=offset)

    sessions = data["sessions"]
    if agent:
        agent_map = {"kilocode": "kilo", "opencode": "opencode"}
        target = agent_map.get(agent.lower(), agent.lower())
        sessions = [s for s in sessions if s.get("agent_type") == target]

    items = [
        SessionItem(
            session_id=s["session_id"],
            project_name=s.get("project_name"),
            agent_type=s.get("agent_type", ""),
            model=s.get("model"),
            start_time=s.get("start_time"),
            end_time=s.get("end_time"),
            message_count=s.get("message_count", 0),
            estimated_tokens=s.get("message_count", 0) * 500,
            estimated_cost=round(
                (s.get("message_count", 0) * 500 / 1_000_000) * 9.0, 4
            ),
        )
        for s in sessions
    ]

    return SessionListResponse(sessions=items, total=data["total"])


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session_detail(session_id: str):
    detail = collect_session_detail(session_id)
    if not detail:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetailResponse(
        session_id=detail["session_id"],
        project_name=detail.get("project_name"),
        agent_type=detail.get("agent_type", ""),
        model=detail.get("model"),
        start_time=detail.get("start_time"),
        end_time=detail.get("end_time"),
        message_count=detail.get("message_count", 0),
        estimated_tokens=detail.get("message_count", 0) * 500,
        estimated_cost=round(
            (detail.get("message_count", 0) * 500 / 1_000_000) * 9.0, 4
        ),
    )


@router.get("/agents", response_model=AgentListResponse)
def get_agents():
    agents = collect_agent_status()
    items = [
        AgentStatusItem(
            name=a["name"],
            type=a["type"],
            status=a["status"],
            active_sessions=a["active_sessions"],
            last_active=a.get("last_active"),
            model=a.get("model"),
        )
        for a in agents
    ]
    return AgentListResponse(agents=items)


@router.get("/token-trend", response_model=TrendResponse)
def get_token_trend(period: str = Query("week")):
    data = collect_all_data(limit=2000)
    trend_data = aggregate_trend(data["sessions"], period)
    items = [
        TrendDataPoint(date=d["date"], kilocode=d["kilocode"], opencode=d["opencode"])
        for d in trend_data
    ]
    return TrendResponse(data=items)


@router.get("/cost-trend", response_model=TrendResponse)
def get_cost_trend(period: str = Query("week")):
    data = collect_all_data(limit=2000)
    trend_data = aggregate_cost_trend(data["sessions"], period)
    items = [
        TrendDataPoint(date=d["date"], kilocode=d["kilocode"], opencode=d["opencode"])
        for d in trend_data
    ]
    return TrendResponse(data=items)


@router.get("/model-breakdown", response_model=ModelBreakdownResponse)
def get_model_breakdown(period: str = Query("week")):
    data = collect_all_data(limit=2000)
    breakdown = compute_model_breakdown(data["sessions"])
    items = [
        ModelBreakdownItem(name=m["name"], count=m["count"], percentage=m["percentage"])
        for m in breakdown
    ]
    return ModelBreakdownResponse(models=items)
