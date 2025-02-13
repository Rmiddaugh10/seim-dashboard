# tests/test_log_ingestion.py
import pytest
from datetime import datetime
from app.services.log_ingestion import LogIngestionService
from app.models.log_entry import LogCreate, LogLevel

@pytest.fixture
async def log_service():
    service = LogIngestionService()
    # Mock elasticsearch client here
    await service.initialize(None)
    return service

async def test_create_log(log_service):
    log_data = LogCreate(
        message="Test log message",
        level=LogLevel.INFO,
        source="test-service",
        host="test-host"
    )
    
    log = await log_service.create_log(log_data)
    assert log is not None
    assert log.message == "Test log message"
    assert log.level == LogLevel.INFO