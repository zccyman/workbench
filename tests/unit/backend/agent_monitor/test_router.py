import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from tools.agent_monitor.router import router

app = FastAPI()
app.include_router(router, prefix="/api/tools/agent-monitor")


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/api/tools/agent-monitor/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "sources" in data


class TestOverviewEndpoint:
    def test_overview_returns_200(self, client):
        response = client.get("/api/tools/agent-monitor/overview")
        assert response.status_code == 200
        data = response.json()
        assert "active_agents" in data
        assert "total_sessions_today" in data


class TestSessionsEndpoint:
    def test_sessions_returns_200(self, client):
        response = client.get("/api/tools/agent-monitor/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data

    def test_sessions_with_limit(self, client):
        response = client.get("/api/tools/agent-monitor/sessions?limit=5")
        assert response.status_code == 200


class TestAgentsEndpoint:
    def test_agents_returns_200(self, client):
        response = client.get("/api/tools/agent-monitor/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data


class TestTokenTrend:
    def test_token_trend_returns_200(self, client):
        response = client.get("/api/tools/agent-monitor/token-trend?period=week")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestCostTrend:
    def test_cost_trend_returns_200(self, client):
        response = client.get("/api/tools/agent-monitor/cost-trend?period=week")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestModelBreakdown:
    def test_model_breakdown_returns_200(self, client):
        response = client.get("/api/tools/agent-monitor/model-breakdown?period=week")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
