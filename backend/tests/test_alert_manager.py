# tests/test_alert_manager.py
import pytest
from datetime import datetime
from app.services.alert_manager import AlertManager
from app.models.alert import AlertCreate, AlertSeverity, AlertSource

@pytest.fixture
async def alert_manager():
    manager = AlertManager()
    # Mock elasticsearch client here
    await manager.initialize(None)
    return manager

async def test_create_alert(alert_manager):
    alert_data = AlertCreate(
        title="Test Alert",
        description="Test Description",
        severity=AlertSeverity.HIGH,
        source=AlertSource.IDS
    )
    
    alert = await alert_manager.create_alert(alert_data)
    assert alert is not None
    assert alert.title == "Test Alert"
    assert alert.severity == AlertSeverity.HIGH