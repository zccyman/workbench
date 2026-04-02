from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import json
from ..database import get_db
from ..models import Message, MessageWithParts, Part

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/session/{session_id}", response_model=list[Message])
def get_messages_by_session(
    session_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    query = """
        SELECT id, session_id, time_created, data
        FROM message
        WHERE session_id = ?
        ORDER BY time_created ASC
    """
    rows = db.execute_query(query, (session_id,))

    messages = []
    for row in rows:
        parsed_data = {}
        try:
            parsed_data = json.loads(row[3])
        except:
            pass

        messages.append(
            Message(id=row[0], session_id=row[1], time_created=row[2], data=row[3])
        )

    return messages


@router.get("/{message_id}", response_model=MessageWithParts)
def get_message(
    message_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    query = """
        SELECT id, session_id, time_created, data
        FROM message
        WHERE id = ?
    """
    row = db.execute_query_one(query, (message_id,))

    if not row:
        raise HTTPException(status_code=404, detail="Message not found")

    parsed_data = {}
    try:
        parsed_data = json.loads(row[3])
    except:
        pass

    parts_query = """
        SELECT id, message_id, session_id, data
        FROM part
        WHERE message_id = ?
    """
    part_rows = db.execute_query(parts_query, (message_id,))

    parts = []
    for part_row in part_rows:
        parts.append(
            Part(
                id=part_row[0],
                message_id=part_row[1],
                session_id=part_row[2],
                data=part_row[3],
            )
        )

    return MessageWithParts(
        id=row[0],
        session_id=row[1],
        time_created=row[2],
        data=row[3],
        parts=parts,
        parsed_data=parsed_data,
    )


@router.get("/session/{session_id}/with-parts", response_model=list[MessageWithParts])
def get_messages_with_parts(
    session_id: str,
    source: str = Query("kilo", description="Data source: kilo or opencode"),
):
    db = get_db(source)

    query = """
        SELECT id, session_id, time_created, data
        FROM message
        WHERE session_id = ?
        ORDER BY time_created ASC
    """
    rows = db.execute_query(query, (session_id,))

    messages = []
    for row in rows:
        parsed_data = {}
        try:
            parsed_data = json.loads(row[3])
        except:
            pass

        parts_query = """
            SELECT id, message_id, session_id, data
            FROM part
            WHERE message_id = ?
        """
        part_rows = db.execute_query(parts_query, (row[0],))

        parts = []
        for part_row in part_rows:
            parts.append(
                Part(
                    id=part_row[0],
                    message_id=part_row[1],
                    session_id=part_row[2],
                    data=part_row[3],
                )
            )

        messages.append(
            MessageWithParts(
                id=row[0],
                session_id=row[1],
                time_created=row[2],
                data=row[3],
                parts=parts,
                parsed_data=parsed_data,
            )
        )

    return messages
