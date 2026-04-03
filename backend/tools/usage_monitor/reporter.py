import json


def _sort_by_value(d: dict) -> list[tuple[str, int]]:
    return sorted(d.items(), key=lambda x: x[1], reverse=True)


def format_markdown(result: dict) -> str:
    parts = [
        "# OpenClaw Usage Report",
        "",
        f"**Period**: {result['date_range']['from']} ~ {result['date_range']['to']}",
        f"**Sessions**: {result['total_sessions']} | **Tool Calls**: {result['total_tool_calls']} | **Skill Reads**: {result['total_skill_reads']}",
        "",
        "## Tool Usage Ranking",
        "",
        "| Rank | Tool | Calls | % |",
        "|------|------|-------|---|",
    ]

    total = result["total_tool_calls"] or 1
    for i, (name, count) in enumerate(_sort_by_value(result["tool_frequency"]), 1):
        pct = (count / total) * 100
        parts.append(f"| {i} | {name} | {count} | {pct:.1f}% |")

    parts.append("")

    if result["skill_frequency"]:
        parts.extend(
            [
                "## Skill Activation Ranking",
                "",
                "| Rank | Skill | Activations |",
                "|------|-------|-------------|",
            ]
        )
        for i, (name, count) in enumerate(_sort_by_value(result["skill_frequency"]), 1):
            parts.append(f"| {i} | {name} | {count} |")
        parts.append("")

    if result["daily_activity"]:
        parts.extend(
            [
                "## Daily Activity",
                "",
                "| Date | Sessions | Tool Calls | Skill Reads |",
                "|------|----------|------------|-------------|",
            ]
        )
        for d in sorted(result["daily_activity"].keys()):
            a = result["daily_activity"][d]
            parts.append(
                f"| {d} | {a['sessions']} | {a['tool_calls']} | {a['skill_reads']} |"
            )
        parts.append("")

    return "\n".join(parts)


def format_json(result: dict) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False)
