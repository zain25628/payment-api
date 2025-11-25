# Refactored by Copilot – Health Tests
from app.config import settings


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"
    assert "service" in body and body["service"] == settings.PROJECT_NAME
    assert "version" in body and body["version"] == settings.PROJECT_VERSION


def test_health_db_endpoint(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "database" in body
