from fastapi import APIRouter, Query, HTTPException
from ..database import db
from ..models import ChatMessage, ChatMessageWithSender

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get(
    "/conversation/{conversation_id}", response_model=list[ChatMessageWithSender]
)
def get_messages_by_conversation(
    conversation_id: str,
    platform: str = Query("wechat"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    before: int = Query(0, description="Messages before this timestamp (ms)"),
    after: int = Query(0, description="Messages after this timestamp (ms)"),
):
    query = """
        SELECT m.*, ct.avatar_url as sender_avatar
        FROM chat_message m
        LEFT JOIN chat_contact ct ON m.sender_id = ct.id AND m.platform = ct.platform
        WHERE m.conversation_id = ? AND m.platform = ?
    """
    params = [conversation_id, platform]

    if before > 0:
        query += " AND m.timestamp < ?"
        params.append(before)
    if after > 0:
        query += " AND m.timestamp > ?"
        params.append(after)

    query += " ORDER BY m.timestamp ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))
    return [
        ChatMessageWithSender(
            id=r["id"],
            platform=r["platform"],
            conversation_id=r["conversation_id"],
            sender_id=r["sender_id"],
            sender_name=r["sender_name"],
            content=r["content"],
            msg_type=r["msg_type"],
            timestamp=r["timestamp"],
            extra_json=r["extra_json"],
            sender_avatar=r["sender_avatar"],
        )
        for r in rows
    ]


@router.get("/{message_id}", response_model=ChatMessage)
def get_message(
    message_id: str,
    platform: str = Query("wechat"),
):
    row = db.execute_query_one(
        "SELECT * FROM chat_message WHERE id = ? AND platform = ?",
        (message_id, platform),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Message not found")

    return ChatMessage(
        id=row["id"],
        platform=row["platform"],
        conversation_id=row["conversation_id"],
        sender_id=row["sender_id"],
        sender_name=row["sender_name"],
        content=row["content"],
        msg_type=row["msg_type"],
        timestamp=row["timestamp"],
        extra_json=row["extra_json"],
    )
