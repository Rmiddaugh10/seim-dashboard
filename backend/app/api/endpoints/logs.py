"""
API endpoints for log management and retrieval.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from elasticsearch import NotFoundError
from ...models.log_entry import LogEntry, LogCreate, LogLevel
from ...services.log_ingestion import LogIngestionService

router = APIRouter()
log_service = LogIngestionService()

@router.get("/", response_model=List[LogEntry])
async def get_logs(
    level: Optional[LogLevel] = None,
    source: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    search_term: Optional[str] = None,
    limit: int = Query(default=50, le=1000),
    skip: int = 0,
):
    """
    Retrieve logs with optional filtering.
    """
    try:
        query = {
            "bool": {
                "must": [{"match_all": {}}]
            }
        }
        
        if level:
            query["bool"]["must"].append({"term": {"level": level}})
            
        if source:
            query["bool"]["must"].append({"term": {"source": source}})
            
        if search_term:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": search_term,
                    "fields": ["message", "host", "source"]
                }
            })
            
        if start_time or end_time:
            time_range = {}
            if start_time:
                time_range["gte"] = start_time.isoformat()
            if end_time:
                time_range["lte"] = end_time.isoformat()
            query["bool"]["must"].append({"range": {"timestamp": time_range}})
        
        return await log_service.get_logs(query, limit, skip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=LogEntry)
async def create_log(log: LogCreate):
    """
    Create a new log entry.
    """
    try:
        return await log_service.create_log(log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=List[LogEntry])
async def create_logs_batch(logs: List[LogCreate]):
    """
    Create multiple log entries in batch.
    """
    try:
        return await log_service.create_logs_batch(logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
async def get_log_sources():
    """
    Get list of unique log sources.
    """
    try:
        return await log_service.get_unique_sources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_log_statistics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """
    Get log statistics and aggregations.
    """
    try:
        return await log_service.get_statistics(start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_logs(
    start_time: datetime,
    end_time: datetime,
    pattern: Optional[str] = None,
):
    """
    Analyze logs for patterns or anomalies.
    """
    try:
        return await log_service.analyze_logs(start_time, end_time, pattern)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/")
async def delete_old_logs(
    older_than: datetime,
):
    """
    Delete logs older than specified date.
    """
    try:
        deleted_count = await log_service.delete_old_logs(older_than)
        return {"status": "success", "deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))