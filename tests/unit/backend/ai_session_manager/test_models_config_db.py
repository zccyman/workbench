"""Tests for ai_session_manager models, config, and database"""
import pytest
import os
import tempfile
from unittest.mock import patch
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "backend"))

from tools.ai_session_manager.models import (
    Session, SessionWithProject, Message, MessageWithParts, Part,
    Project, ProjectWithSessions, SearchResult, StatsOverview, StatsTrend,
    ProjectStats, KnowledgeExtraction, TabContent, TabContentCreate,
    TabContentWithStats, TabContentMessage, timestamp_to_str, str_to_timestamp,
)
from tools.ai_session_manager.config import Config, config
from tools.ai_session_manager.database import Database


class TestModels:
    """Test Pydantic models"""

    def test_session_base(self):
        s = Session(
            id="sess_001",
            project_id="proj_001",
            title="Test Session",
            directory="/home/user/project",
            time_created=1700000000000,
            time_updated=1700000100000,
        )
        assert s.id == "sess_001"
        assert s.title == "Test Session"

    def test_session_with_project(self):
        s = SessionWithProject(
            id="sess_001",
            project_id="proj_001",
            title="Test",
            directory="/home/user/project",
            time_created=1700000000000,
            time_updated=1700000100000,
            project_name="MyProject",
            message_count=5,
        )
        assert s.project_name == "MyProject"
        assert s.message_count == 5

    def test_message(self):
        m = Message(
            id="msg_001",
            session_id="sess_001",
            time_created=1700000000000,
            data='{"role": "user", "content": "Hello"}',
        )
        assert m.session_id == "sess_001"

    def test_message_with_parts(self):
        part = Part(
            id="part_001",
            message_id="msg_001",
            session_id="sess_001",
            data='{"text": "Hello"}',
        )
        m = MessageWithParts(
            id="msg_001",
            session_id="sess_001",
            time_created=1700000000000,
            data='{"role": "user", "content": "Hello"}',
            parts=[part],
            parsed_data={"role": "user", "content": "Hello"},
        )
        assert len(m.parts) == 1
        assert m.parsed_data["role"] == "user"

    def test_project_with_sessions(self):
        p = ProjectWithSessions(
            id="proj_001",
            worktree="/home/user/project",
            name="MyProject",
            session_count=10,
            time_created=1700000000000,
            time_updated=1700000100000,
        )
        assert p.session_count == 10

    def test_search_result(self):
        sr = SearchResult(
            session_id="sess_001",
            session_title="Test",
            message_id="msg_001",
            snippet="Hello world",
            highlights=["Hello"],
        )
        assert "Hello" in sr.highlights

    def test_stats_overview(self):
        stats = StatsOverview(
            total_sessions=100,
            total_messages=500,
            total_projects=10,
            total_parts=200,
            sessions_this_week=5,
            sessions_this_month=20,
        )
        assert stats.total_sessions == 100

    def test_stats_trend(self):
        trend = StatsTrend(date="2026-04-01", count=5)
        assert trend.date == "2026-04-01"
        assert trend.count == 5

    def test_project_stats(self):
        ps = ProjectStats(
            project_id="proj_001",
            project_name="MyProject",
            session_count=10,
            message_count=50,
        )
        assert ps.message_count == 50

    def test_knowledge_extraction(self):
        ke = KnowledgeExtraction(
            session_id="sess_001",
            technical_solutions=["Used FastAPI"],
            decisions=["Chose SQLite"],
            lessons_learned=["Keep it simple"],
            key_files=["main.py"],
        )
        assert len(ke.technical_solutions) == 1

    def test_tab_content(self):
        msg = TabContentMessage(role="user", content="Hello")
        tc = TabContent(
            id="tab_001",
            title="Test Tab",
            url="http://example.com",
            markdown="# Test",
            messages=[msg],
            source="tabbit",
            created_at=1700000000000,
            updated_at=1700000100000,
        )
        assert tc.id == "tab_001"
        assert len(tc.messages) == 1

    def test_tab_content_with_stats(self):
        tc = TabContentWithStats(
            id="tab_001",
            title="Test",
            markdown="# Test",
            messages=[],
            created_at=1700000000000,
            updated_at=1700000100000,
            message_count=0,
            char_count=6,
        )
        assert tc.char_count == 6

    def test_timestamp_to_str(self):
        result = timestamp_to_str(1700000000000)
        assert "2023" in result

    def test_str_to_timestamp(self):
        result = str_to_timestamp("2023-11-14T00:00:00")
        assert result > 0

    def test_str_to_timestamp_invalid(self):
        result = str_to_timestamp("invalid")
        assert result == 0

    def test_timestamp_to_str_invalid(self):
        result = timestamp_to_str("not_a_number")
        assert result == "not_a_number"


class TestConfig:
    """Test configuration"""

    def test_config_default_paths(self):
        assert "kilo.db" in Config.KILO_CODE_DB_PATH
        assert "opencode.db" in Config.OPENCODE_DB_PATH

    def test_get_db_path_kilo(self):
        path = Config.get_db_path("kilo")
        assert "kilo.db" in path

    def test_get_db_path_opencode(self):
        path = Config.get_db_path("opencode")
        assert "opencode.db" in path

    def test_get_db_path_default(self):
        path = Config.get_db_path("unknown")
        assert "kilo.db" in path

    def test_get_available_sources_no_db(self):
        with patch.object(Config, 'KILO_CODE_DB_PATH', '/nonexistent/path'):
            with patch.object(Config, 'OPENCODE_DB_PATH', '/nonexistent/path2'):
                sources = config.get_available_sources()
                assert sources == []


class TestDatabase:
    """Test database wrapper"""

    @pytest.fixture
    def db(self, temp_db_path):
        return Database(temp_db_path)

    def test_execute_query_empty(self, db):
        result = db.execute_query("SELECT * FROM session")
        assert result == []

    def test_execute_query_one_empty(self, db):
        result = db.execute_query_one("SELECT * FROM session WHERE id = ?", ("nonexistent",))
        assert result is None

    def test_execute_write(self, db):
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS test_table (id TEXT PRIMARY KEY, name TEXT)
        """)
        db.execute_write(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            ("1", "test"),
        )
        result = db.execute_query("SELECT * FROM test_table")
        assert len(result) == 1
        assert result[0][1] == "test"

    def test_get_tables(self, db):
        tables = db.get_tables()
        assert len(tables) > 0

    def test_get_table_schema(self, db):
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS test_schema (id TEXT PRIMARY KEY, name TEXT)
        """)
        schema = db.get_table_schema("test_schema")
        assert len(schema) > 0

    def test_get_connection_context_manager(self, db):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
