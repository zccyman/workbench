import os
import json
from ..config import config
from ..database import db


def import_feishu_data(app_id: str = "", app_secret: str = "") -> dict:
    if not app_id or not app_secret:
        return {
            "status": "error",
            "message": "Feishu App ID and Secret required. Set FEISHU_APP_ID/FEISHU_APP_SECRET env vars.",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
        }

    total = 0
    imported = 0
    failed = 0
    errors = []

    try:
        import lark_oapi as lark
        from lark_oapi.api.im.v1 import *
    except ImportError:
        return {
            "status": "error",
            "message": "lark-oapi not installed. Run: pip install lark-oapi",
            "total": 0,
            "imported": 0,
            "failed": 0,
            "errors": ["lark-oapi not available"],
        }

    client = lark.Client.builder().app_id(app_id).app_secret(app_secret).build()

    import time

    now = int(time.time() * 1000)

    try:
        chat_request = ListChatRequest.builder().page_size(50).build()
        chat_response = client.im.v1.chat.list(chat_request)

        if not chat_response.success():
            return {
                "status": "error",
                "message": f"Failed to list chats: {chat_response.msg}",
                "total": 0,
                "imported": 0,
                "failed": 1,
                "errors": [chat_response.msg],
            }

        chats = (
            chat_response.data.items
            if chat_response.data and chat_response.data.items
            else []
        )
        total = len(chats)

        for chat in chats:
            try:
                db.execute_write(
                    """INSERT OR REPLACE INTO chat_contact
                    (id, platform, name, type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat.chat_id, "feishu", chat.name or "", "group", now, now),
                )

                db.execute_write(
                    """INSERT OR REPLACE INTO chat_conversation
                    (id, platform, contact_id, title, last_message_time, message_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        chat.chat_id,
                        "feishu",
                        chat.chat_id,
                        chat.name or "",
                        None,
                        0,
                        now,
                        now,
                    ),
                )

                msg_request = (
                    ListMessageRequest.builder()
                    .container_id_type("chat")
                    .container_id(chat.chat_id)
                    .page_size(50)
                    .build()
                )
                msg_response = client.im.v1.message.list(msg_request)

                if (
                    msg_response.success()
                    and msg_response.data
                    and msg_response.data.items
                ):
                    for msg in msg_response.data.items:
                        content_text = _extract_feishu_content(msg)
                        db.execute_write(
                            """INSERT OR REPLACE INTO chat_message
                            (id, platform, conversation_id, sender_id, sender_name, content, msg_type, timestamp, extra_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                msg.message_id,
                                "feishu",
                                chat.chat_id,
                                msg.sender.sender_id.open_id
                                if msg.sender and msg.sender.sender_id
                                else None,
                                msg.sender.sender_id.open_id
                                if msg.sender and msg.sender.sender_id
                                else None,
                                content_text,
                                msg.msg_type or "text",
                                int(msg.create_time) if msg.create_time else now,
                                None,
                            ),
                        )
                imported += 1
            except Exception as e:
                failed += 1
                errors.append(f"Chat {chat.chat_id}: {str(e)}")

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "total": total,
            "imported": imported,
            "failed": failed,
            "errors": errors,
        }

    return {
        "status": "completed",
        "total": total,
        "imported": imported,
        "failed": failed,
        "errors": errors,
    }


def _extract_feishu_content(msg) -> str:
    try:
        if msg.body and msg.body.content:
            content = msg.body.content
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed.get("text", content)
            except (json.JSONDecodeError, Exception):
                pass
            return content
    except Exception:
        pass
    return ""
