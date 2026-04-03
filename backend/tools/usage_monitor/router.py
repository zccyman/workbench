import json
import os
from pathlib import Path
from fastapi import APIRouter, Query

from .models import (
    AnalysisRequest,
    AnalysisResponse,
    SummaryResponse,
    ToolUsageItem,
    SkillUsageItem,
    HourlyDataItem,
    DailyActivityItem,
    MarkdownReportResponse,
    ConfigResponse,
)
from .collector import collect_events, _get_default_agent_dir
from .analyzer import analyze
from .reporter import format_markdown, format_json

router = APIRouter(tags=["usage-monitor"])


def _run_analysis(req: AnalysisRequest) -> dict:
    agent_dir = req.agent_dir or os.path.join(
        Path.home(), ".openclaw", "agents", req.agent_name
    )
    tool_calls, skill_reads, sessions = collect_events(
        agent_dir, req.from_date, req.to_date
    )
    return analyze(tool_calls, skill_reads, sessions, req.period)


def _to_response(raw: dict) -> AnalysisResponse:
    total_calls = raw["total_tool_calls"] or 1
    return AnalysisResponse(
        summary=SummaryResponse(
            total_sessions=raw["total_sessions"],
            total_tool_calls=raw["total_tool_calls"],
            total_skill_reads=raw["total_skill_reads"],
            date_range_from=raw["date_range"]["from"],
            date_range_to=raw["date_range"]["to"],
        ),
        tool_frequency=[
            ToolUsageItem(
                rank=i + 1,
                tool_name=name,
                calls=count,
                percentage=round((count / total_calls) * 100, 1),
            )
            for i, (name, count) in enumerate(
                sorted(raw["tool_frequency"].items(), key=lambda x: x[1], reverse=True)
            )
        ],
        skill_frequency=[
            SkillUsageItem(rank=i + 1, skill_name=name, activations=count)
            for i, (name, count) in enumerate(
                sorted(raw["skill_frequency"].items(), key=lambda x: x[1], reverse=True)
            )
        ],
        hourly_distribution=[
            HourlyDataItem(hour=h, calls=raw["hourly_distribution"].get(h, 0))
            for h in range(24)
        ],
        daily_activity=[
            DailyActivityItem(date=d, **v)
            for d, v in sorted(raw["daily_activity"].items())
        ],
    )


@router.get("/analyze", response_model=AnalysisResponse)
def get_analyze(
    agent_dir: str = Query(""),
    agent_name: str = Query("bot1"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    period: str = Query("all"),
):
    req = AnalysisRequest(
        agent_dir=agent_dir,
        agent_name=agent_name,
        from_date=from_date,
        to_date=to_date,
        period=period,
    )
    raw = _run_analysis(req)
    return _to_response(raw)


@router.post("/analyze", response_model=AnalysisResponse)
def post_analyze(req: AnalysisRequest):
    raw = _run_analysis(req)
    return _to_response(raw)


@router.get("/report/markdown", response_model=MarkdownReportResponse)
def get_report_markdown(
    agent_dir: str = Query(""),
    agent_name: str = Query("bot1"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    period: str = Query("all"),
):
    req = AnalysisRequest(
        agent_dir=agent_dir,
        agent_name=agent_name,
        from_date=from_date,
        to_date=to_date,
        period=period,
    )
    raw = _run_analysis(req)
    return MarkdownReportResponse(content=format_markdown(raw))


@router.get("/report/json")
def get_report_json(
    agent_dir: str = Query(""),
    agent_name: str = Query("bot1"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    period: str = Query("all"),
):
    req = AnalysisRequest(
        agent_dir=agent_dir,
        agent_name=agent_name,
        from_date=from_date,
        to_date=to_date,
        period=period,
    )
    raw = _run_analysis(req)
    return json.loads(format_json(raw))


@router.get("/config", response_model=ConfigResponse)
def get_config():
    default_dir = _get_default_agent_dir()
    agents = []
    base = Path.home() / ".openclaw" / "agents"
    if base.exists():
        agents = [d.name for d in base.iterdir() if d.is_dir()]
    return ConfigResponse(default_agent_dir=default_dir, available_agents=agents)
