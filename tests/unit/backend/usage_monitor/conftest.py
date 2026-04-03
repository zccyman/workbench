import pytest
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return str(FIXTURES_DIR)


@pytest.fixture
def mock_collect(fixtures_dir):
    from tools.usage_monitor.collector import collect_events

    return lambda from_date=None, to_date=None: collect_events(
        fixtures_dir, from_date, to_date
    )
