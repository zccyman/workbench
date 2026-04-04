"""Pydantic models for Agent Monitor API responses."""

from pydantic import BaseModel
from typing import Optional, List


# ── Overview ──────────────────────────────────────────────


class OverviewResponse(BaseModel):
    active_agents: int
    total_sessions_today: int
    total_sessions_week: int
    estimated_tokens_today: int
    estimated_cost_today: float
    most_used_model: str


# ── Sessions ──────────────────────────────────────────────


class SessionItem(BaseModel):
    session_id: str
    project_name: Optional[str] = None
    agent_type: str  # "kilocode" | "opencode"
    model: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    message_count: int = 0
    estimated_tokens: int = 0
    estimated_cost: float = 0.0


class SessionListResponse(BaseModel):
    sessions: List[SessionItem]
    total: int


class SessionDetailResponse(SessionItem):
    messages: Optional[List[dict]] = None


# ── Agents ────────────────────────────────────────────────


class AgentStatusItem(BaseModel):
    name: str
    type: str  # "kilocode" | "opencode"
    status: str  # "running" | "idle" | "offline"
    active_sessions: int
    last_active: Optional[str] = None
    model: Optional[str] = None


class AgentListResponse(BaseModel):
    agents: List[AgentStatusItem]


# ── Trends ────────────────────────────────────────────────


class TrendDataPoint(BaseModel):
    date: str
    kilocode: float = 0
    opencode: float = 0


class TrendResponse(BaseModel):
    data: List[TrendDataPoint]


# ── Model Breakdown ───────────────────────────────────────


class ModelBreakdownItem(BaseModel):
    name: str
    count: int
    percentage: float


class ModelBreakdownResponse(BaseModel):
    models: List[ModelBreakdownItem]


# ── Health ────────────────────────────────────────────────


class HealthSourceStatus(BaseModel):
    ai_session_manager: str = "unknown"
    usage_monitor: str = "unknown"
    database: str = "unknown"


class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    sources: HealthSourceStatus
