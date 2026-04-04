import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from tools.agent_monitor.collector import (
    _detect_model_from_session,
    _check_process_running,
)


class TestResolveModel:
    def test_claude_detection(self):
        row = {"title": "claude-sonnet-4 session", "directory": ""}
        result = _detect_model_from_session(row)
        assert "claude" in (result or "").lower()

    def test_glm_detection(self):
        row = {"title": "glm-4.7 session", "directory": ""}
        result = _detect_model_from_session(row)
        assert "glm" in (result or "").lower()

    def test_no_detection_returns_none(self):
        row = {"title": "regular session", "directory": ""}
        result = _detect_model_from_session(row)
        assert result is None


class TestCheckProcessRunning:
    def test_nonexistent_process(self):
        result = _check_process_running("this_process_definitely_does_not_exist_xyz123")
        assert result is False
