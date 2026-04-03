import pytest
from pathlib import Path


class TestCollector:
    def test_collect_all_events(self, mock_collect):
        tool_calls, skill_reads, sessions = mock_collect()
        assert len(tool_calls) == 6
        assert len(skill_reads) == 3
        assert len(sessions) == 2

    def test_tool_names_extracted(self, mock_collect):
        tool_calls, _, _ = mock_collect()
        names = [tc["tool_name"] for tc in tool_calls]
        assert "read" in names
        assert "bash" in names
        assert "write" in names

    def test_skill_reads_from_skill_md(self, mock_collect):
        _, skill_reads, _ = mock_collect()
        skill_names = [sr["skill_name"] for sr in skill_reads]
        assert "cartography" in skill_names
        assert "frontend-design" in skill_names
        assert "dev-workflow" in skill_names

    def test_session_info(self, mock_collect):
        _, _, sessions = mock_collect()
        assert len(sessions) == 2
        assert sessions[0]["session_id"] == "session1"
        assert sessions[1]["session_id"] == "session2"

    def test_empty_dir(self):
        from tools.usage_monitor.collector import collect_events

        tool_calls, skill_reads, sessions = collect_events("/nonexistent/path")
        assert tool_calls == []
        assert skill_reads == []
        assert sessions == []

    def test_date_filter_from(self, mock_collect):
        tool_calls, _, _ = mock_collect(from_date="2026-04-02")
        for tc in tool_calls:
            assert tc["timestamp"][:10] >= "2026-04-02"

    def test_date_filter_to(self, mock_collect):
        tool_calls, _, _ = mock_collect(to_date="2026-04-01")
        for tc in tool_calls:
            assert tc["timestamp"][:10] <= "2026-04-01"


class TestAnalyzer:
    def _sample_data(self):
        from tools.usage_monitor.collector import collect_events

        fixtures = str(Path(__file__).parent / "fixtures")
        return collect_events(fixtures)

    def test_tool_frequency(self):
        tc, sr, sess = self._sample_data()
        from tools.usage_monitor.analyzer import analyze

        result = analyze(tc, sr, sess)
        assert result["tool_frequency"]["read"] == 3
        assert result["tool_frequency"]["bash"] == 2
        assert result["tool_frequency"]["write"] == 1

    def test_skill_frequency(self):
        tc, sr, sess = self._sample_data()
        from tools.usage_monitor.analyzer import analyze

        result = analyze(tc, sr, sess)
        assert result["skill_frequency"]["cartography"] == 1
        assert result["skill_frequency"]["frontend-design"] == 1
        assert result["skill_frequency"]["dev-workflow"] == 1

    def test_hourly_distribution(self):
        tc, sr, sess = self._sample_data()
        from tools.usage_monitor.analyzer import analyze

        result = analyze(tc, sr, sess)
        assert len(result["hourly_distribution"]) == 24
        assert result["hourly_distribution"][10] == 4
        assert result["hourly_distribution"][14] == 2

    def test_total_counts(self):
        tc, sr, sess = self._sample_data()
        from tools.usage_monitor.analyzer import analyze

        result = analyze(tc, sr, sess)
        assert result["total_sessions"] == 2
        assert result["total_tool_calls"] == 6
        assert result["total_skill_reads"] == 3

    def test_date_range(self):
        tc, sr, sess = self._sample_data()
        from tools.usage_monitor.analyzer import analyze

        result = analyze(tc, sr, sess)
        assert result["date_range"]["from"] == "2026-04-01"
        assert result["date_range"]["to"] == "2026-04-02"

    def test_empty_data(self):
        from tools.usage_monitor.analyzer import analyze

        result = analyze([], [], [])
        assert result["total_sessions"] == 0
        assert result["total_tool_calls"] == 0
        assert result["total_skill_reads"] == 0
        assert result["tool_frequency"] == {}
        assert result["skill_frequency"] == {}


class TestReporter:
    def _sample_result(self):
        return {
            "tool_frequency": {"read": 3, "bash": 2, "write": 1},
            "skill_frequency": {"cartography": 1, "frontend-design": 1},
            "hourly_distribution": {h: 0 for h in range(24)},
            "daily_activity": {
                "2026-04-01": {"sessions": 1, "tool_calls": 4, "skill_reads": 2}
            },
            "total_sessions": 1,
            "total_tool_calls": 6,
            "total_skill_reads": 2,
            "date_range": {"from": "2026-04-01", "to": "2026-04-01"},
        }

    def test_markdown_format(self):
        from tools.usage_monitor.reporter import format_markdown

        md = format_markdown(self._sample_result())
        assert "OpenClaw Usage Report" in md
        assert "Tool Usage Ranking" in md
        assert "read" in md

    def test_json_format(self):
        from tools.usage_monitor.reporter import format_json
        import json

        j = format_json(self._sample_result())
        parsed = json.loads(j)
        assert parsed["total_tool_calls"] == 6
