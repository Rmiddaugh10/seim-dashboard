"""
Alert data models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class AlertSource(str, Enum):
    IDS = "ids"
    FIREWALL = "firewall"
    ANTIVIRUS = "antivirus"
    AUTHENTICATION = "authentication"
    SYSTEM = "system"
    APPLICATION = "application"
    CUSTOM = "custom"

class AlertBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    severity: AlertSeverity
    source: AlertSource
    tags: List[str] = Field(default_factory=list)

class AlertCreate(AlertBase):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    affected_assets: List[str] = Field(default_factory=list)
    raw_data: Optional[dict] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None

class Alert(AlertBase):
    id: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.NEW
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    affected_assets: List[str] = []
    raw_data: Optional[dict] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True