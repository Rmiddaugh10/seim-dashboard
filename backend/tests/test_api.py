# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "SIEM Dashboard"}

def test_get_alerts():
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_logs():
    response = client.get("/api/v1/logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_metrics():
    response = client.get("/api/v1/metrics/dashboard")
    assert response.status_code == 200
    assert "securityScore" in response.json()