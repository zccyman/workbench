from fastapi import APIRouter, Query, HTTPException
from ..database import get_db
from ..models import Project, ProjectWithSessions

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectWithSessions])
def list_projects(
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    query = """
        SELECT p.id, p.worktree, p.name,
               (SELECT COUNT(*) FROM session WHERE project_id = p.id) as session_count,
               p.time_created, p.time_updated
        FROM project p
        ORDER BY p.name, p.worktree
    """
    rows = db.execute_query(query)

    projects = []
    for row in rows:
        # name is often null, use worktree basename as fallback
        name = row[2]
        if not name and row[1]:
            name = row[1].rstrip('/').split('/')[-1]
        if not name:
            name = 'Unknown'
        
        projects.append(
            ProjectWithSessions(
                id=row[0],
                worktree=row[1],
                name=name,
                session_count=row[3],
                time_created=row[4],
                time_updated=row[5],
            )
        )

    return projects


@router.get("/{project_id}", response_model=ProjectWithSessions)
def get_project(
    project_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    query = """
        SELECT p.id, p.worktree, p.name,
               (SELECT COUNT(*) FROM session WHERE project_id = p.id) as session_count,
               p.time_created, p.time_updated
        FROM project p
        WHERE p.id = ?
    """
    row = db.execute_query_one(query, (project_id,))

    if not row:
        raise HTTPException(status_code=404, detail="Project not found")

    name = row[2]
    if not name and row[1]:
        name = row[1].rstrip('/').split('/')[-1]
    if not name:
        name = 'Unknown'

    return ProjectWithSessions(
        id=row[0],
        worktree=row[1],
        name=name,
        session_count=row[3],
        time_created=row[4],
        time_updated=row[5],
    )
