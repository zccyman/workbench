"""Tests for ai_session_manager services"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "backend"))

from tools.ai_session_manager.services.export_service import (
    export_session_markdown,
    export_session_json,
    export_batch_markdown,
    export_all_to_directory,
    _sanitize_filename,
)
from tools.ai_session_manager.services.knowledge_service import (
    extract_knowledge,
    _extract_technical_solutions,
    _extract_decisions,
    _extract_lessons,
    _extract_key_files,
    clear_cache,
)
from tools.ai_session_manager.services.search_service import (
    search_sessions,
    search_in_session,
)


class TestExportService:
    """Test export service functions"""

    def test_sanitize_filename_basic(self):
        result = _sanitize_filename("Hello World")
        assert result == "Hello-World"

    def test_sanitize_filename_special_chars(self):
        result = _sanitize_filename('file<>:"/\\|?*.txt')
        assert "<" not in result
        assert ">" not in result
        assert "/" not in result

    def test_sanitize_filename_max_length(self):
        long_name = "a" * 200
        result = _sanitize_filename(long_name)
        assert len(result) <= 80

    def test_sanitize_filename_empty(self):
        result = _sanitize_filename("")
        assert result == "untitled"

    def test_export_session_markdown(self, populated_db):
        with patch(
            "tools.ai_session_manager.services.export_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            md = export_session_markdown("sess_001", "kilo")
            assert "Test Session 1" in md
            assert "Hello world" in md

    def test_export_session_markdown_not_found(self, populated_db):
        with patch(
            "tools.ai_session_manager.services.export_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            md = export_session_markdown("nonexistent", "kilo")
            assert md == ""

    def test_export_session_json(self, populated_db):
        with patch(
            "tools.ai_session_manager.services.export_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            data = export_session_json("sess_001", "kilo")
            assert "session" in data
            assert "messages" in data
            assert len(data["messages"]) == 2

    def test_export_session_json_not_found(self, populated_db):
        with patch(
            "tools.ai_session_manager.services.export_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            data = export_session_json("nonexistent", "kilo")
            assert data == {}

    def test_export_all_to_directory(self, populated_db):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "tools.ai_session_manager.services.export_service.get_db"
            ) as mock_get_db:
                from tools.ai_session_manager.database import Database

                mock_get_db.return_value = Database(populated_db)
                result = export_all_to_directory("kilo", tmpdir)
                assert result["total"] == 2
                assert result["exported"] >= 0
                assert result["failed"] >= 0

    def test_export_all_to_directory_empty(self, temp_db_path):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "tools.ai_session_manager.services.export_service.get_db"
            ) as mock_get_db:
                from tools.ai_session_manager.database import Database

                mock_get_db.return_value = Database(temp_db_path)
                result = export_all_to_directory("kilo", tmpdir)
                assert result["total"] == 0


class TestKnowledgeService:
    """Test knowledge extraction service"""

    def test_extract_technical_solutions(self):
        content = "The solution is to use a function that implements the code fix"
        result = _extract_technical_solutions(content)
        assert len(result) > 0

    def test_extract_decisions(self):
        content = "We decided to use FastAPI for the architecture design"
        result = _extract_decisions(content)
        assert len(result) > 0

    def test_extract_lessons(self):
        content = "Important: remember to always test the code, it is better to be safe"
        result = _extract_lessons(content)
        assert len(result) > 0

    def test_extract_key_files(self):
        content = "Check the files main.py and utils/helper.py for the implementation"
        result = _extract_key_files(content)
        assert "main.py" in result

    def test_extract_knowledge(self, populated_db):
        clear_cache()
        with patch(
            "tools.ai_session_manager.services.knowledge_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            result = extract_knowledge("sess_001", "kilo")
            assert result.session_id == "sess_001"

    def test_extract_knowledge_cache(self, populated_db):
        clear_cache()
        with patch(
            "tools.ai_session_manager.services.knowledge_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            result1 = extract_knowledge("sess_001", "kilo")
            result2 = extract_knowledge("sess_001", "kilo")
            assert result1 is result2

    def test_extract_knowledge_not_found(self, populated_db):
        clear_cache()
        with patch(
            "tools.ai_session_manager.services.knowledge_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            result = extract_knowledge("nonexistent", "kilo")
            assert result.session_id == "nonexistent"
            assert result.technical_solutions == []

    def test_clear_cache(self):
        import tools.ai_session_manager.services.knowledge_service as ks

        ks.knowledge_cache["test"] = "value"
        clear_cache()
        assert len(ks.knowledge_cache) == 0


class TestSearchService:
    """Test search service functions"""

    def test_search_sessions(self, populated_db):
        with patch(
            "tools.ai_session_manager.services.search_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            results = search_sessions("Hello", "kilo")
            assert isinstance(results, list)

    def test_search_sessions_no_results(self, populated_db):
        with patch(
            "tools.ai_session_manager.services.search_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            results = search_sessions("nonexistent_xyz_123", "kilo")
            assert results == []

    def test_search_in_session(self, populated_db):
        with patch(
            "tools.ai_session_manager.services.search_service.get_db"
        ) as mock_get_db:
            from tools.ai_session_manager.database import Database

            mock_get_db.return_value = Database(populated_db)
            results = search_in_session("sess_001", "Hello", "kilo")
            assert isinstance(results, list)
