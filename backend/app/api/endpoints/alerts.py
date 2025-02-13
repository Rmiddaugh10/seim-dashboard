"""
API endpoints for alert management and retrieval.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from elasticsearch import NotFoundError
from ...core.config import settings
from ...models.alert import Alert, AlertCreate, AlertUpdate, AlertSeverity
from fastapi import Request
from ...services.alert_manager import AlertManager

router = APIRouter()
alert_manager = AlertManager()

@router.get("/", response_model=List[Alert])
async def get_alerts(
    severity: Optional[AlertSeverity] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(default=50, le=100),
    skip: int = 0,
):
    """
    Retrieve alerts with optional filtering.
    """
    try:
        query = {
            "bool": {
                "must": [{"match_all": {}}]
            }
        }
        
        if severity:
            query["bool"]["must"].append({"term": {"severity": severity}})
            
        if start_time or end_time:
            time_range = {}
            if start_time:
                time_range["gte"] = start_time.isoformat()
            if end_time:
                time_range["lte"] = end_time.isoformat()
            query["bool"]["must"].append({"range": {"timestamp": time_range}})
        
        return await alert_manager.get_alerts(query, limit, skip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Alert)
async def create_alert(alert: AlertCreate):
    """
    Create a new alert.
    """
    try:
        return await alert_manager.create_alert(alert)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """
    Retrieve a specific alert by ID.
    """
    try:
        alert = await alert_manager.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{alert_id}", response_model=Alert)
async def update_alert(alert_id: str, alert_update: AlertUpdate):
    """
    Update an existing alert.
    """
    try:
        updated_alert = await alert_manager.update_alert(alert_id, alert_update)
        if not updated_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return updated_alert
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """
    Delete an alert.
    """
    try:
        success = await alert_manager.delete_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"status": "success", "message": "Alert deleted"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """
    Acknowledge an alert.
    """
    try:
        alert = await alert_manager.acknowledge_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/summary")
async def get_alert_statistics():
    """
    Get alert statistics summary.
    """
    try:
        stats = await alert_manager.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))