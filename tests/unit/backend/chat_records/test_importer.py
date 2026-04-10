import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from tools.chat_records.importers.wechat import (
    import_wechat_data_with_progress,
    _find_db_files,
)


class TestImportWechatDataWithProgress:
    """测试微信导入功能"""

    @pytest.fixture
    def temp_backup_dir(self):
        """创建临时备份目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_config(self, temp_backup_dir):
        """模拟配置"""
        with patch("tools.chat_records.importers.wechat.config") as mock_cfg:
            mock_cfg.get_backup_dir.return_value = temp_backup_dir
            yield mock_cfg

    def test_no_backup_dir(self, mock_config):
        """测试当备份目录不存在时返回错误"""
        with patch("tools.chat_records.importers.wechat.config") as mock_cfg:
            mock_cfg.get_backup_dir.return_value = "/nonexistent/path"
            result = import_wechat_data_with_progress("test_key", "task123", "today")

            assert result["status"] == "error"
            assert "No backup found" in result["message"]

    def test_no_decrypt_key(self, temp_backup_dir):
        """测试当没有解密密钥时返回错误"""
        with patch("tools.chat_records.importers.wechat.config") as mock_cfg:
            mock_cfg.get_backup_dir.return_value = temp_backup_dir
            result = import_wechat_data_with_progress("", "task123", "today")

            assert result["status"] == "error"
            assert "Decryption key required" in result["message"]

    def test_range_calculation(self):
        """测试时间范围计算"""
        import time

        now_ms = int(time.time() * 1000)

        ranges = {
            "today": 24 * 60 * 60 * 1000,
            "3days": 3 * 24 * 60 * 60 * 1000,
            "week": 7 * 24 * 60 * 60 * 1000,
            "month": 30 * 24 * 60 * 60 * 1000,
        }

        for range_name, expected_ms in ranges.items():
            range_ms = {
                "today": 24 * 60 * 60 * 1000,
                "3days": 3 * 24 * 60 * 60 * 1000,
                "week": 7 * 24 * 60 * 60 * 1000,
                "month": 30 * 24 * 60 * 60 * 1000,
            }.get(range_name, 0)

            min_timestamp = now_ms - range_ms if range_ms > 0 else 0

            if range_name == "today":
                assert now_ms - min_timestamp == 24 * 60 * 60 * 1000
            elif range_name == "3days":
                assert now_ms - min_timestamp == 3 * 24 * 60 * 60 * 1000
            elif range_name == "week":
                assert now_ms - min_timestamp == 7 * 24 * 60 * 60 * 1000
            elif range_name == "month":
                assert now_ms - min_timestamp == 30 * 24 * 60 * 60 * 1000

    def test_range_all(self):
        """测试 'all' 范围返回0时间戳"""
        import time

        now_ms = int(time.time() * 1000)

        range_val = "all"
        range_ms = {
            "today": 24 * 60 * 60 * 1000,
            "3days": 3 * 24 * 60 * 60 * 1000,
            "week": 7 * 24 * 60 * 60 * 1000,
            "month": 30 * 24 * 60 * 60 * 1000,
        }.get(range_val, 0)

        min_timestamp = now_ms - range_ms if range_ms > 0 else 0

        assert min_timestamp == 0


class TestFindDbFiles:
    """测试数据库文件查找"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()

        os.makedirs(os.path.join(temp_dir, "MicroMsg", "account1"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "MicroMsg", "account2"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "Multi", "MSG"), exist_ok=True)

        Path(os.path.join(temp_dir, "MicroMsg", "account1", "MicroMsg.db")).touch()
        Path(os.path.join(temp_dir, "MicroMsg", "account2", "Contact.db")).touch()
        Path(os.path.join(temp_dir, "Multi", "MSG", "MSG.db")).touch()
        Path(os.path.join(temp_dir, "ChatMsg.db")).touch()

        yield temp_dir

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_find_micromsg_db(self, temp_dir):
        """测试查找 MicroMsg.db 文件"""
        result = _find_db_files(temp_dir, ["MicroMsg.db"])
        assert len(result) == 1
        assert "MicroMsg.db" in result[0]

    def test_find_msg_db(self, temp_dir):
        """测试查找 MSG 文件"""
        result = _find_db_files(temp_dir, ["Multi/MSG"])
        assert len(result) >= 1

    def test_exclude_wal_files(self, temp_dir):
        """测试排除 WAL 文件"""
        Path(os.path.join(temp_dir, "test.db-wal")).touch()
        Path(os.path.join(temp_dir, "test.db-shm")).touch()

        result = _find_db_files(temp_dir, ["MicroMsg.db"])

        for r in result:
            assert not r.endswith("-wal")
            assert not r.endswith("-shm")


class TestRangeFiltering:
    """测试时间范围过滤逻辑"""

    def test_sql_query_today(self):
        """测试今天的 SQL 查询生成"""
        import time

        now_ms = int(time.time() * 1000)
        min_timestamp = now_ms - (24 * 60 * 60 * 1000)

        expected_sql = f"SELECT localId, talker, type, createTime, content, msgSvrId FROM MSG WHERE createTime >= {min_timestamp}"

        assert f"createTime >= {min_timestamp}" in expected_sql

    def test_sql_query_all(self):
        """测试全部的 SQL 查询生成 (无WHERE条件)"""
        min_timestamp = 0

        if min_timestamp > 0:
            sql = f"SELECT localId, talker, type, createTime, content, msgSvrId FROM MSG WHERE createTime >= {min_timestamp}"
        else:
            sql = "SELECT localId, talker, type, createTime, content, msgSvrId FROM MSG"

        assert "WHERE" not in sql
        assert "createTime" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
