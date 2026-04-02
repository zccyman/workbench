from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SessionBase(BaseModel):
    project_id: str
    title: str
    directory: str


class Session(SessionBase):
    id: str
    time_created: int
    time_updated: int

    class Config:
        from_attributes = True


class SessionWithProject(Session):
    message_count: Optional[int] = None
    project_name: Optional[str] = None
    time_created_str: Optional[str] = None
    time_updated_str: Optional[str] = None


class Part(BaseModel):
    id: str
    message_id: str
    session_id: str
    data: str
    time_created: Optional[int] = None

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    session_id: str
    time_created: int
    data: str


class Message(MessageBase):
    id: str

    class Config:
        from_attributes = True


class MessageWithParts(Message):
    parts: Optional[List[Part]] = None
    parsed_data: Optional[dict] = None


class ProjectBase(BaseModel):
    name: Optional[str] = None
    worktree: str


class Project(ProjectBase):
    id: str

    class Config:
        from_attributes = True


class ProjectWithSessions(Project):
    session_count: Optional[int] = None
    time_created: Optional[int] = None
    time_updated: Optional[int] = None


class SearchResult(BaseModel):
    session_id: str
    session_title: str
    message_id: str
    snippet: str
    highlights: List[str] = []


class StatsOverview(BaseModel):
    total_sessions: int
    total_messages: int
    total_projects: int
    total_parts: int
    sessions_this_week: int
    sessions_this_month: int


class StatsTrend(BaseModel):
    date: str
    count: int


class ProjectStats(BaseModel):
    project_id: str
    project_name: str
    session_count: int
    message_count: int


class KnowledgeExtraction(BaseModel):
    session_id: str
    technical_solutions: List[str] = []
    decisions: List[str] = []
    lessons_learned: List[str] = []
    key_files: List[str] = []


class ExportRequest(BaseModel):
    session_ids: List[str]


class ExportResponse(BaseModel):
    files: List[dict]


class TabContentMessage(BaseModel):
    role: str
    content: str


class TabContentBase(BaseModel):
    title: str
    url: Optional[str] = None
    markdown: str
    messages: List[TabContentMessage] = []
    source: str = "tabbit"


class TabContentCreate(TabContentBase):
    pass


class TabContent(TabContentBase):
    id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class TabContentWithStats(TabContent):
    message_count: Optional[int] = None
    char_count: Optional[int] = None
    created_at_str: Optional[str] = None
    updated_at_str: Optional[str] = None


def timestamp_to_str(ts: int) -> str:
    """Convert millisecond timestamp to ISO string."""
    try:
        return datetime.fromtimestamp(ts / 1000).isoformat()
    except:
        return str(ts)


def str_to_timestamp(s: str) -> int:
    """Convert ISO string to millisecond timestamp."""
    try:
        return int(datetime.fromisoformat(s).timestamp() * 1000)
    except:
        return 0
