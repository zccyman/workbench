from fastapi import APIRouter, Query, HTTPException
from ..database import get_db
from ..models import StatsOverview, StatsTrend, ProjectStats
from datetime import datetime

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/overview", response_model=StatsOverview)
def get_stats_overview(
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    total_sessions = db.execute_query_one("SELECT COUNT(*) FROM session")[0]
    total_messages = db.execute_query_one("SELECT COUNT(*) FROM message")[0]
    total_projects = db.execute_query_one("SELECT COUNT(*) FROM project")[0]
    total_parts = db.execute_query_one("SELECT COUNT(*) FROM part")[0]

    now_ts = int(datetime.now().timestamp() * 1000)
    week_ago = now_ts - (7 * 24 * 60 * 60 * 1000)
    month_ago = now_ts - (30 * 24 * 60 * 60 * 1000)

    sessions_this_week = db.execute_query_one(
        "SELECT COUNT(*) FROM session WHERE time_created >= ?", (week_ago,)
    )[0]

    sessions_this_month = db.execute_query_one(
        "SELECT COUNT(*) FROM session WHERE time_created >= ?", (month_ago,)
    )[0]

    return StatsOverview(
        total_sessions=total_sessions,
        total_messages=total_messages,
        total_projects=total_projects,
        total_parts=total_parts,
        sessions_this_week=sessions_this_week,
        sessions_this_month=sessions_this_month,
    )


@router.get("/trends", response_model=list[StatsTrend])
def get_stats_trends(
    source: str = Query("kilo", description="Data source: kilo or opencode"),
    days: int = Query(30, ge=1, le=365),
):
    db = get_db(source)

    now_ts = int(datetime.now().timestamp() * 1000)
    start_ts = now_ts - (days * 24 * 60 * 60 * 1000)

    query = """
        SELECT time_created FROM session
        WHERE time_created >= ?
    """
    rows = db.execute_query(query, (start_ts,))

    date_counts = {}
    for row in rows:
        ts = row[0]
        date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
        date_counts[date_str] = date_counts.get(date_str, 0) + 1

    trends = []
    for date, count in sorted(date_counts.items()):
        trends.append(StatsTrend(date=date, count=count))

    return trends


@router.get("/projects", response_model=list[ProjectStats])
def get_stats_by_project(
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    query = """
        SELECT p.id as project_id, p.name as project_name,
               COUNT(s.id) as session_count
        FROM project p
        LEFT JOIN session s ON p.id = s.project_id
        GROUP BY p.id
        ORDER BY session_count DESC
    """
    rows = db.execute_query(query)

    stats = []
    for row in rows:
        project_id = row[0]
        message_count = db.execute_query_one(
            "SELECT COUNT(*) FROM message m JOIN session s ON m.session_id = s.id WHERE s.project_id = ?",
            (project_id,),
        )[0]

        project_name = row[1] or "Unnamed"
        if not project_name or project_name == "None":
            project_name = row[0][:8]

        stats.append(
            ProjectStats(
                project_id=project_id,
                project_name=project_name,
                session_count=row[2],
                message_count=message_count,
            )
        )

    return stats


@router.get("/messages", response_model=dict)
def get_message_stats(
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    avg_result = db.execute_query_one(
        "SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM message GROUP BY session_id)"
    )
    avg_messages_per_session = (
        round(avg_result[0], 2) if avg_result and avg_result[0] else 0
    )

    total_parts = db.execute_query_one("SELECT COUNT(*) FROM part")[0]

    return {
        "avg_messages_per_session": avg_messages_per_session,
        "total_parts": total_parts,
    }
