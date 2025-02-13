"""
Log entry data models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogBase(BaseModel):
    message: str = Field(..., min_length=1)
    level: LogLevel = LogLevel.INFO
    source: str = Field(..., min_length=1)
    host: Optional[str] = None

class LogCreate(LogBase):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    tags: list[str] = Field(default_factory=list)

class LogEntry(LogBase):
    id: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    processed: bool = False
    correlation_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class LogStatistics(BaseModel):
    total_logs: int
    logs_by_level: Dict[LogLevel, int]
    logs_by_source: Dict[str, int]
    time_range: Dict[str, datetime]
    processing_status: Dict[str, int]

class LogAnalysis(BaseModel):
    patterns: Dict[str, int]
    anomalies: list[Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: list[str]