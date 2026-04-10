from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..database import db
from ..models import ChatContact

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=list[ChatContact])
def list_contacts(
    platform: str = Query("wechat", description="Platform: wechat, qq, feishu"),
    type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    query = "SELECT * FROM chat_contact WHERE platform = ?"
    params = [platform]

    if type:
        query += " AND type = ?"
        params.append(type)

    query += " ORDER BY updated_at DESC NULLS LAST LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))
    return [
        ChatContact(
            id=r["id"],
            platform=r["platform"],
            name=r["name"],
            alias=r["alias"],
            remark=r["remark"],
            type=r["type"],
            avatar_url=r["avatar_url"],
            extra_json=r["extra_json"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/{contact_id}", response_model=ChatContact)
def get_contact(
    contact_id: str,
    platform: str = Query("wechat"),
):
    row = db.execute_query_one(
        "SELECT * FROM chat_contact WHERE id = ? AND platform = ?",
        (contact_id, platform),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")

    return ChatContact(
        id=row["id"],
        platform=row["platform"],
        name=row["name"],
        alias=row["alias"],
        remark=row["remark"],
        type=row["type"],
        avatar_url=row["avatar_url"],
        extra_json=row["extra_json"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.get("/search/{query}", response_model=list[ChatContact])
def search_contacts(
    query: str,
    platform: str = Query("wechat"),
    limit: int = Query(50, ge=1, le=200),
):
    search_term = f"%{query}%"
    rows = db.execute_query(
        """SELECT * FROM chat_contact
        WHERE platform = ? AND (name LIKE ? OR alias LIKE ? OR remark LIKE ?)
        ORDER BY updated_at DESC NULLS LAST LIMIT ?""",
        (platform, search_term, search_term, search_term, limit),
    )
    return [
        ChatContact(
            id=r["id"],
            platform=r["platform"],
            name=r["name"],
            alias=r["alias"],
            remark=r["remark"],
            type=r["type"],
            avatar_url=r["avatar_url"],
            extra_json=r["extra_json"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]
