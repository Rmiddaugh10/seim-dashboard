# tests/test_threat_detection.py
import pytest
from datetime import datetime, timedelta
from app.services.threat_detection import ThreatDetectionService

@pytest.fixture
async def threat_service():
    service = ThreatDetectionService()
    # Mock elasticsearch client here
    await service.initialize(None)
    return service

async def test_calculate_security_score(threat_service):
    score = await threat_service.calculate_security_score()
    assert score is not None
    assert "overall_score" in score
    assert 0 <= score["overall_score"] <= 100