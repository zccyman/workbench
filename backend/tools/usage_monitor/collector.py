"""Collector: Parse OpenClaw session JSONL files to extract tool calls and skill reads."""

import json
import os
from pathlib import Path
from typing import Optional


def _get_default_agent_dir() -> str:
    return str(Path.home() / ".openclaw" / "agents" / "bot1")


def collect_events(
    agent_dir: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse all .jsonl files in sessions directory.

    Returns:
        (tool_calls, skill_reads, sessions)
    """
    if not agent_dir:
        agent_dir = _get_default_agent_dir()

    sessions_dir = Path(agent_dir) / "sessions"
    if not sessions_dir.exists():
        return [], [], []

    tool_calls: list[dict] = []
    skill_reads: list[dict] = []
    sessions: list[dict] = []

    jsonl_files = sorted(sessions_dir.glob("*.jsonl"))

    for jsonl_path in jsonl_files:
        session_id = jsonl_path.stem
        session_start = ""
        session_end = ""
        session_tool_count = 0

        try:
            content = jsonl_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            timestamp = obj.get("timestamp")
            if not timestamp:
                continue

            if not session_start:
                session_start = timestamp
            session_end = timestamp

            if (
                obj.get("type") == "message"
                and obj.get("message", {}).get("role") == "assistant"
            ):
                message_content = obj["message"].get("content", [])
                if isinstance(message_content, list):
                    for c in message_content:
                        if isinstance(c, dict) and c.get("type") == "toolCall":
                            tool_name = c.get("name", "unknown")
                            args = c.get("arguments", {})

                            if from_date and timestamp[:10] < from_date:
                                continue
                            if to_date and timestamp[:10] > to_date:
                                continue

                            tool_calls.append(
                                {
                                    "timestamp": timestamp,
                                    "tool_name": tool_name,
                                    "arguments": args,
                                    "session_id": session_id,
                                }
                            )
                            session_tool_count += 1

                            if tool_name == "read":
                                file_path = (
                                    args.get("file_path", "")
                                    or args.get("path", "")
                                    or args.get("file", "")
                                )
                                if (
                                    isinstance(file_path, str)
                                    and "SKILL.md" in file_path
                                ):
                                    skill_name = file_path
                                    skills_idx = file_path.find("skills/")
                                    if skills_idx != -1:
                                        after_skills = file_path[skills_idx + 7 :]
                                        skill_name = (
                                            after_skills.split("/")[0] or after_skills
                                        )

                                    skill_reads.append(
                                        {
                                            "timestamp": timestamp,
                                            "skill_name": skill_name,
                                            "skill_path": file_path,
                                            "session_id": session_id,
                                        }
                                    )

        if session_start:
            sessions.append(
                {
                    "session_id": session_id,
                    "start_time": session_start,
                    "end_time": session_end,
                    "tool_call_count": session_tool_count,
                }
            )

    return tool_calls, skill_reads, sessions
