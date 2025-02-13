"""
API endpoints for security metrics and analytics.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ...services.threat_detection import ThreatDetectionService

router = APIRouter()
metrics_service = ThreatDetectionService()

@router.get("/dashboard")
async def get_dashboard_metrics(
    time_range: Optional[str] = Query(
        default="24h",
        regex="^(1h|12h|24h|7d|30d)$"
    )
):
    """
    Get aggregated metrics for dashboard display.
    """
    try:
        time_ranges = {
            "1h": timedelta(hours=1),
            "12h": timedelta(hours=12),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        end_time = datetime.utcnow()
        start_time = end_time - time_ranges[time_range]
        
        return await metrics_service.get_dashboard_metrics(start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threats/summary")
async def get_threat_summary(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """
    Get summary of detected threats.
    """
    try:
        return await metrics_service.get_threat_summary(start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/trends")
async def get_alert_trends(
    interval: str = Query(
        default="1h",
        regex="^(1h|1d|1w)$"
    ),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """
    Get alert trends over time.
    """
    try:
        return await metrics_service.get_alert_trends(interval, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security-score")
async def get_security_score():
    """
    Calculate overall security score based on various metrics.
    """
    try:
        return await metrics_service.calculate_security_score()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-threats")
async def get_top_threats(
    limit: int = Query(default=10, le=50),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """
    Get top security threats.
    """
    try:
        return await metrics_service.get_top_threats(limit, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies")
async def get_anomalies(
    sensitivity: float = Query(default=0.75, ge=0, le=1),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """
    Detect and return security anomalies.
    """
    try:
        return await metrics_service.detect_anomalies(sensitivity, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance")
async def get_compliance_metrics():
    """
    Get security compliance metrics.
    """
    try:
        return await metrics_service.get_compliance_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geographic")
async def get_geographic_metrics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """
    Get geographic distribution of security events.
    """
    try:
        return await metrics_service.get_geographic_metrics(start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))