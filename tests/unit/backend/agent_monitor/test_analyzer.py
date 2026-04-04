import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from tools.agent_monitor.analyzer import (
    estimate_tokens,
    estimate_cost,
    compute_overview,
    aggregate_trend,
    aggregate_cost_trend,
    compute_model_breakdown,
)


class TestEstimateTokens:
    def test_zero_messages(self):
        assert estimate_tokens(0) == 0

    def test_default_tokens_per_message(self):
        assert estimate_tokens(1) == 500

    def test_multiple_messages(self):
        assert estimate_tokens(10) == 5000

    def test_large_count(self):
        assert estimate_tokens(1000) == 500_000


class TestEstimateCost:
    def test_free_model(self):
        cost = estimate_cost(10_000, "minimax-m2.5")
        assert cost == 0.0

    def test_claude_sonnet(self):
        cost = estimate_cost(1_000_000, "claude-sonnet-4-20250514")
        assert cost == pytest.approx(9.0)

    def test_glm_model(self):
        cost = estimate_cost(1_000_000, "glm-4.7")
        assert cost == pytest.approx(3.0)

    def test_unknown_model_uses_fallback(self):
        cost = estimate_cost(1_000_000, "unknown-model")
        assert cost == pytest.approx(9.0)

    def test_no_model_uses_fallback(self):
        cost = estimate_cost(1_000_000)
        assert cost == pytest.approx(9.0)

    def test_partial_model_match(self):
        cost = estimate_cost(1_000_000, "claude-sonnet-something")
        assert cost == pytest.approx(9.0)


class TestComputeOverview:
    def test_empty_sessions(self):
        result = compute_overview([])
        assert result["total_sessions_today"] == 0
        assert result["estimated_tokens_today"] == 0
        assert result["estimated_cost_today"] == 0.0

    def test_with_sessions(self):
        from datetime import datetime

        now = datetime.now().isoformat()
        sessions = [
            {
                "session_id": "s1",
                "agent_type": "kilo",
                "model": "minimax-m2.5",
                "message_count": 10,
                "start_time": now,
            }
        ]
        result = compute_overview(sessions)
        assert result["total_sessions_today"] == 1
        assert result["estimated_tokens_today"] == 5000


class TestAggregateTrend:
    def test_empty_sessions(self):
        result = aggregate_trend([], "week")
        assert len(result) == 7

    def test_groups_by_date(self):
        sessions = [
            {
                "session_id": "s1",
                "agent_type": "kilo",
                "model": "glm-4.7",
                "message_count": 10,
                "start_time": "2026-04-01T10:00:00",
            },
            {
                "session_id": "s2",
                "agent_type": "opencode",
                "model": "glm-4.7",
                "message_count": 5,
                "start_time": "2026-04-01T11:00:00",
            },
        ]
        result = aggregate_trend(sessions, "week")
        day_entry = next((d for d in result if d["date"] == "2026-04-01"), None)
        assert day_entry is not None
        assert day_entry["kilocode"] == 5000
        assert day_entry["opencode"] == 2500


class TestAggregateCostTrend:
    def test_empty_sessions(self):
        result = aggregate_cost_trend([], "week")
        assert len(result) == 7

    def test_free_model_costs_nothing(self):
        sessions = [
            {
                "session_id": "s1",
                "agent_type": "kilo",
                "model": "minimax-m2.5",
                "message_count": 100,
                "start_time": "2026-04-01T10:00:00",
            }
        ]
        result = aggregate_cost_trend(sessions, "week")
        day_entry = next((d for d in result if d["date"] == "2026-04-01"), None)
        assert day_entry["kilocode"] == 0.0


class TestModelBreakdown:
    def test_empty_sessions(self):
        result = compute_model_breakdown([])
        assert result == []

    def test_single_model(self):
        sessions = [
            {"model": "glm-4.7", "agent_type": "opencode"},
            {"model": "glm-4.7", "agent_type": "opencode"},
        ]
        result = compute_model_breakdown(sessions)
        assert len(result) == 1
        assert result[0]["name"] == "glm-4.7"
        assert result[0]["count"] == 2
        assert result[0]["percentage"] == 100.0

    def test_multiple_models(self):
        sessions = [
            {"model": "glm-4.7"},
            {"model": "claude-sonnet-4-20250514"},
            {"model": "glm-4.7"},
        ]
        result = compute_model_breakdown(sessions)
        assert len(result) == 2
        assert result[0]["name"] == "glm-4.7"
        assert result[0]["count"] == 2
        assert result[0]["percentage"] == pytest.approx(66.7)
        assert result[1]["name"] == "claude-sonnet-4-20250514"
        assert result[1]["count"] == 1
