"""Pydantic models for Usage Monitor API."""

from pydantic import BaseModel
from typing import Optional


class AnalysisRequest(BaseModel):
    agent_dir: str = ""
    agent_name: str = "bot1"
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    period: str = "all"


class SummaryResponse(BaseModel):
    total_sessions: int
    total_tool_calls: int
    total_skill_reads: int
    date_range_from: str
    date_range_to: str


class ToolUsageItem(BaseModel):
    rank: int
    tool_name: str
    calls: int
    percentage: float


class SkillUsageItem(BaseModel):
    rank: int
    skill_name: str
    activations: int


class HourlyDataItem(BaseModel):
    hour: int
    calls: int


class DailyActivityItem(BaseModel):
    date: str
    sessions: int
    tool_calls: int
    skill_reads: int


class AnalysisResponse(BaseModel):
    summary: SummaryResponse
    tool_frequency: list[ToolUsageItem]
    skill_frequency: list[SkillUsageItem]
    hourly_distribution: list[HourlyDataItem]
    daily_activity: list[DailyActivityItem]


class MarkdownReportResponse(BaseModel):
    content: str


class ConfigResponse(BaseModel):
    default_agent_dir: str
    available_agents: list[str]
