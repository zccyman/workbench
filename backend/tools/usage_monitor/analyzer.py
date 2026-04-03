from datetime import datetime, timedelta
from collections import Counter


def analyze(
    tool_calls: list[dict],
    skill_reads: list[dict],
    sessions: list[dict],
    period: str = "all",
) -> dict:
    tool_freq = dict(Counter(tc["tool_name"] for tc in tool_calls))

    skill_freq = dict(Counter(sr["skill_name"] for sr in skill_reads))

    hourly = {h: 0 for h in range(24)}
    for tc in tool_calls:
        try:
            hour = datetime.fromisoformat(tc["timestamp"]).hour
            hourly[hour] += 1
        except (ValueError, TypeError):
            pass

    daily = {}
    for s in sessions:
        date = s["start_time"][:10]
        if date not in daily:
            daily[date] = {"sessions": 0, "tool_calls": 0, "skill_reads": 0}
        daily[date]["sessions"] += 1
        daily[date]["tool_calls"] += s["tool_call_count"]

    for sr in skill_reads:
        date = sr["timestamp"][:10]
        if date not in daily:
            daily[date] = {"sessions": 0, "tool_calls": 0, "skill_reads": 0}
        daily[date]["skill_reads"] += 1

    sorted_dates = sorted(daily.keys())
    date_range_from = sorted_dates[0] if sorted_dates else ""
    date_range_to = sorted_dates[-1] if sorted_dates else ""

    if period != "all":
        now = datetime.now()
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start = now - timedelta(days=7)
        elif period == "monthly":
            start = (
                now.replace(month=now.month - 1)
                if now.month > 1
                else now.replace(year=now.year - 1, month=12)
            )
        else:
            start = datetime.min
        start_str = start.strftime("%Y-%m-%d")
        daily = {d: v for d, v in daily.items() if d >= start_str}

    return {
        "tool_frequency": tool_freq,
        "skill_frequency": skill_freq,
        "hourly_distribution": hourly,
        "daily_activity": daily,
        "total_sessions": len(sessions),
        "total_tool_calls": len(tool_calls),
        "total_skill_reads": len(skill_reads),
        "date_range": {"from": date_range_from, "to": date_range_to},
    }
