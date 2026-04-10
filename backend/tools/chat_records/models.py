from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatContact(BaseModel):
    id: str
    platform: str
    name: Optional[str] = None
    alias: Optional[str] = None
    remark: Optional[str] = None
    type: str = "user"
    avatar_url: Optional[str] = None
    extra_json: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    class Config:
        from_attributes = True


class ChatConversation(BaseModel):
    id: str
    platform: str
    contact_id: Optional[str] = None
    title: Optional[str] = None
    last_message_time: Optional[int] = None
    message_count: int = 0
    extra_json: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    class Config:
        from_attributes = True


class ChatConversationWithContact(ChatConversation):
    contact_name: Optional[str] = None
    last_message_preview: Optional[str] = None


class ChatMessage(BaseModel):
    id: str
    platform: str
    conversation_id: str
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    content: Optional[str] = None
    msg_type: str = "text"
    timestamp: int
    extra_json: Optional[str] = None

    class Config:
        from_attributes = True


class ChatMessageWithSender(ChatMessage):
    sender_avatar: Optional[str] = None


class BackupResult(BaseModel):
    platform: str
    status: str = "completed"
    total_files: int = 0
    new_files: int = 0
    updated_files: int = 0
    skipped_files: int = 0
    total_size: int = 0
    duration_ms: int = 0
    message: str = ""


class DeleteSourceResult(BaseModel):
    platform: str
    status: str = "completed"
    deleted_files: int = 0
    failed_files: int = 0
    freed_size: int = 0
    errors: List[str] = []


class BackupMeta(BaseModel):
    platform: str
    last_backup: Optional[str] = None
    last_backup_status: Optional[str] = None
    total_backups: int = 0
    files: dict = {}
    source_deleted: bool = False
    last_delete_time: Optional[str] = None


class BackupHistoryEntry(BaseModel):
    timestamp: str
    platform: str
    status: str
    new_files: int
    updated_files: int
    skipped_files: int
    total_size: int


class SourceStatus(BaseModel):
    platform: str
    source_dir: str
    backup_dir: str
    source_exists: bool = False
    backup_exists: bool = False
    last_backup: Optional[str] = None
    backup_file_count: int = 0
    backup_total_size: int = 0
    source_deleted: bool = False


class SearchResult(BaseModel):
    message_id: str
    conversation_id: str
    platform: str
    sender_name: Optional[str] = None
    snippet: str
    timestamp: int
    highlights: List[str] = []


class StatsOverview(BaseModel):
    total_contacts: int
    total_conversations: int
    total_messages: int
    platform_stats: dict = {}


class ImportRequest(BaseModel):
    platform: str
    decrypt_key: Optional[str] = None


class ImportProgress(BaseModel):
    task_id: str
    status: str
    platform: str
    total: int = 0
    imported: int = 0
    failed: int = 0
    errors: List[str] = []
    result: Optional[dict] = None
    processed: int = 0
    total_messages: int = 0
    current_file: str = ""


class DeleteSourceRequest(BaseModel):
    confirm_name: str


def timestamp_to_str(ts: int) -> str:
    try:
        return datetime.fromtimestamp(ts / 1000).isoformat()
    except Exception:
        return str(ts)
