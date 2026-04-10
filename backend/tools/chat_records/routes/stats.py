from fastapi import APIRouter, Query
from ..database import db
from ..models import StatsOverview

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/overview", response_model=StatsOverview)
def get_overview(
    platform: str = Query("wechat"),
):
    total_contacts = db.execute_query_one(
        "SELECT COUNT(*) FROM chat_contact WHERE platform = ?",
        (platform,),
    )[0]

    total_conversations = db.execute_query_one(
        "SELECT COUNT(*) FROM chat_conversation WHERE platform = ?",
        (platform,),
    )[0]

    total_messages = db.execute_query_one(
        "SELECT COUNT(*) FROM chat_message WHERE platform = ?",
        (platform,),
    )[0]

    platform_stats = {}
    from ..config import config

    for p in config.PLATFORMS:
        msg_count = db.execute_query_one(
            "SELECT COUNT(*) FROM chat_message WHERE platform = ?",
            (p,),
        )[0]
        conv_count = db.execute_query_one(
            "SELECT COUNT(*) FROM chat_conversation WHERE platform = ?",
            (p,),
        )[0]
        contact_count = db.execute_query_one(
            "SELECT COUNT(*) FROM chat_contact WHERE platform = ?",
            (p,),
        )[0]
        platform_stats[p] = {
            "messages": msg_count,
            "conversations": conv_count,
            "contacts": contact_count,
        }

    return StatsOverview(
        total_contacts=total_contacts,
        total_conversations=total_conversations,
        total_messages=total_messages,
        platform_stats=platform_stats,
    )


@router.get("/by-date")
def get_stats_by_date(
    platform: str = Query("wechat"),
    days: int = Query(30, ge=1, le=365),
):
    import time

    now_ts = int(time.time() * 1000)
    start_ts = now_ts - (days * 24 * 60 * 60 * 1000)

    rows = db.execute_query(
        "SELECT timestamp FROM chat_message WHERE platform = ? AND timestamp >= ?",
        (platform, start_ts),
    )

    from datetime import datetime

    date_counts = {}
    for r in rows:
        ts = r["timestamp"]
        date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
        date_counts[date_str] = date_counts.get(date_str, 0) + 1

    return [{"date": d, "count": c} for d, c in sorted(date_counts.items())]


@router.get("/top-senders")
def get_top_senders(
    platform: str = Query("wechat"),
    limit: int = Query(20, ge=1, le=100),
):
    rows = db.execute_query(
        """SELECT sender_name, COUNT(*) as msg_count
        FROM chat_message
        WHERE platform = ? AND sender_name IS NOT NULL
        GROUP BY sender_name
        ORDER BY msg_count DESC
        LIMIT ?""",
        (platform, limit),
    )
    return [
        {"sender_name": r["sender_name"], "message_count": r["msg_count"]} for r in rows
    ]
