from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..database import db
from ..models import ChatConversation, ChatConversationWithContact

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ChatConversationWithContact])
def list_conversations(
    platform: str = Query("wechat"),
    contact_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = """
        SELECT c.*, ct.name as contact_name
        FROM chat_conversation c
        LEFT JOIN chat_contact ct ON c.contact_id = ct.id AND c.platform = ct.platform
        WHERE c.platform = ?
    """
    params = [platform]

    if contact_id:
        query += " AND c.contact_id = ?"
        params.append(contact_id)

    query += " ORDER BY c.last_message_time DESC NULLS LAST LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))
    results = []
    for r in rows:
        last_msg = db.execute_query_one(
            "SELECT content FROM chat_message WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 1",
            (r["id"],),
        )
        results.append(
            ChatConversationWithContact(
                id=r["id"],
                platform=r["platform"],
                contact_id=r["contact_id"],
                title=r["title"],
                last_message_time=r["last_message_time"],
                message_count=r["message_count"] or 0,
                extra_json=r["extra_json"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                contact_name=r["contact_name"],
                last_message_preview=last_msg["content"][:100]
                if last_msg and last_msg["content"]
                else None,
            )
        )
    return results


@router.get("/{conversation_id}", response_model=ChatConversationWithContact)
def get_conversation(
    conversation_id: str,
    platform: str = Query("wechat"),
):
    row = db.execute_query_one(
        """SELECT c.*, ct.name as contact_name
        FROM chat_conversation c
        LEFT JOIN chat_contact ct ON c.contact_id = ct.id AND c.platform = ct.platform
        WHERE c.id = ? AND c.platform = ?""",
        (conversation_id, platform),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Conversation not found")

    last_msg = db.execute_query_one(
        "SELECT content FROM chat_message WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 1",
        (conversation_id,),
    )

    return ChatConversationWithContact(
        id=row["id"],
        platform=row["platform"],
        contact_id=row["contact_id"],
        title=row["title"],
        last_message_time=row["last_message_time"],
        message_count=row["message_count"] or 0,
        extra_json=row["extra_json"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        contact_name=row["contact_name"],
        last_message_preview=last_msg["content"][:100]
        if last_msg and last_msg["content"]
        else None,
    )
