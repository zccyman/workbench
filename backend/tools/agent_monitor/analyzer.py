from datetime import datetime, timedelta
from typing import Optional

from .collector import (
    collect_all_data,
    collect_agent_status,
    MODEL_DEFAULT_TOKENS_PER_MESSAGE,
)

MODEL_PRICES = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-5-20251022": {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "claude-sonnet": {"input": 3.00, "output": 15.00},
    "claude-opus": {"input": 15.00, "output": 75.00},
    "glm-4.7": {"input": 1.00, "output": 5.00},
    "glm-4.6": {"input": 1.00, "output": 5.00},
    "glm": {"input": 1.00, "output": 5.00},
    "minimax-m2.5": {"input": 0.00, "output": 0.00},
    "minimax": {"input": 0.00, "output": 0.00},
    "gpt-5.3-codex": {"input": 2.50, "output": 12.50},
    "gpt": {"input": 2.50, "output": 12.50},
    "codex": {"input": 2.50, "output": 12.50},
    "gemini-2.5-pro": {"input": 2.50, "output": 10.00},
    "gemini": {"input": 2.50, "output": 10.00},
}

FALLBACK_PRICE = {"input": 3.00, "output": 15.00}


def _resolve_model_price(model: Optional[str]) -> dict:
    if not model:
        return FALLBACK_PRICE
    model_lower = model.lower()
    if model_lower in MODEL_PRICES:
        return MODEL_PRICES[model_lower]
    for key, price in MODEL_PRICES.items():
        if key in model_lower:
            return price
    return FALLBACK_PRICE


def estimate_tokens(message_count: int, model: Optional[str] = None) -> int:
    return message_count * MODEL_DEFAULT_TOKENS_PER_MESSAGE


def estimate_cost(tokens: int, model: Optional[str] = None) -> float:
    price = _resolve_model_price(model)
    avg_price = (price["input"] + price["output"]) / 2
    return (tokens / 1_000_000) * avg_price


def compute_overview(sessions: list[dict]) -> dict:
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    today_sessions = []
    week_sessions = []
    today_tokens = 0
    today_cost = 0.0
    model_counts: dict[str, int] = {}

    for s in sessions:
        start = s.get("start_time") or ""
        session_date = None
        try:
            session_date = datetime.fromisoformat(start[:19]).date()
        except (ValueError, TypeError):
            pass

        tokens = estimate_tokens(s.get("message_count", 0), s.get("model"))
        cost = estimate_cost(tokens, s.get("model"))

        if session_date == today:
            today_sessions.append(s)
            today_tokens += tokens
            today_cost += cost

        if session_date and session_date >= week_ago:
            week_sessions.append(s)

        model = s.get("model") or "unknown"
        model_counts[model] = model_counts.get(model, 0) + 1

    agents = collect_agent_status()
    active_agents = sum(1 for a in agents if a["status"] in ("running", "idle"))

    most_used = max(model_counts, key=model_counts.get) if model_counts else "unknown"

    return {
        "active_agents": active_agents,
        "total_sessions_today": len(today_sessions),
        "total_sessions_week": len(week_sessions),
        "estimated_tokens_today": today_tokens,
        "estimated_cost_today": round(today_cost, 4),
        "most_used_model": most_used,
    }


def _get_period_dates(period: str) -> tuple[datetime, datetime]:
    today = datetime.now().date()
    if period == "week":
        start = today - timedelta(days=6)
    elif period == "month":
        start = today - timedelta(days=29)
    else:
        start = today - timedelta(days=6)
    return datetime.combine(start, datetime.min.time()), datetime.combine(
        today, datetime.max.time()
    )


def aggregate_trend(sessions: list[dict], period: str = "week") -> list[dict]:
    start_dt, end_dt = _get_period_dates(period)
    days = (end_dt.date() - start_dt.date()).days + 1
    daily: dict[str, dict[str, float]] = {}

    for i in range(days):
        d = start_dt.date() + timedelta(days=i)
        daily[d.isoformat()] = {"kilocode": 0, "opencode": 0}

    for s in sessions:
        start = s.get("start_time") or ""
        try:
            session_date = datetime.fromisoformat(start[:19]).date()
        except (ValueError, TypeError):
            continue

        date_key = session_date.isoformat()
        if date_key not in daily:
            continue

        tokens = estimate_tokens(s.get("message_count", 0), s.get("model"))
        agent_type = s.get("agent_type", "")

        if agent_type == "kilo":
            daily[date_key]["kilocode"] += tokens
        elif agent_type == "opencode":
            daily[date_key]["opencode"] += tokens

    return [
        {"date": d, "kilocode": round(v["kilocode"]), "opencode": round(v["opencode"])}
        for d, v in sorted(daily.items())
    ]


def aggregate_cost_trend(sessions: list[dict], period: str = "week") -> list[dict]:
    start_dt, end_dt = _get_period_dates(period)
    days = (end_dt.date() - start_dt.date()).days + 1
    daily: dict[str, dict[str, float]] = {}

    for i in range(days):
        d = start_dt.date() + timedelta(days=i)
        daily[d.isoformat()] = {"kilocode": 0.0, "opencode": 0.0}

    for s in sessions:
        start = s.get("start_time") or ""
        try:
            session_date = datetime.fromisoformat(start[:19]).date()
        except (ValueError, TypeError):
            continue

        date_key = session_date.isoformat()
        if date_key not in daily:
            continue

        tokens = estimate_tokens(s.get("message_count", 0), s.get("model"))
        cost = estimate_cost(tokens, s.get("model"))
        agent_type = s.get("agent_type", "")

        if agent_type == "kilo":
            daily[date_key]["kilocode"] += cost
        elif agent_type == "opencode":
            daily[date_key]["opencode"] += cost

    return [
        {
            "date": d,
            "kilocode": round(v["kilocode"], 4),
            "opencode": round(v["opencode"], 4),
        }
        for d, v in sorted(daily.items())
    ]


def compute_model_breakdown(sessions: list[dict]) -> list[dict]:
    model_counts: dict[str, int] = {}
    for s in sessions:
        model = s.get("model") or "unknown"
        model_counts[model] = model_counts.get(model, 0) + 1

    total = sum(model_counts.values())
    if total == 0:
        return []

    return sorted(
        [
            {
                "name": name,
                "count": count,
                "percentage": round((count / total) * 100, 1),
            }
            for name, count in model_counts.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )
