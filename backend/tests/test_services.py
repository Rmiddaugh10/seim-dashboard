# tests/test_services.py
import pytest
from app.services.alert_manager import AlertManager
from app.services.log_ingestion import LogIngestionService
from app.services.threat_detection import ThreatDetectionService
from app.models.alert import AlertCreate, AlertSeverity
from datetime import datetime

@pytest.mark.asyncio
async def test_alert_manager():
    manager = AlertManager()
    await manager.initialize(None)  # Mock ES client for testing
    
    alert = await manager.create_alert(
        AlertCreate(
            title="Test Alert",
            description="Test Description",
            severity=AlertSeverity.HIGH,
            source="test"
        )
    )
    assert alert is not None
    assert alert.title == "Test Alert"

@pytest.mark.asyncio
async def test_log_ingestion():
    service = LogIngestionService()
    await service.initialize(None)  # Mock ES client for testing
    
    stats = await service.get_statistics()
    assert stats is not None
    assert "total_logs" in stats

@pytest.mark.asyncio
async def test_threat_detection():
    service = ThreatDetectionService()
    await service.initialize(None)  # Mock ES client for testing
    
    score = await service.calculate_security_score()
    assert score is not None
    assert 0 <= score["overall_score"] <= 100