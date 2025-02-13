"""
Alert management service.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from elasticsearch import NotFoundError
from ..models.alert import Alert, AlertCreate, AlertUpdate, AlertStatus
from ..core.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.index = "alerts"
        self.es_client = None  # Will be initialized in startup
        
    async def initialize(self, es_client):
        """Initialize the alert manager with elasticsearch client."""
        self.es_client = es_client
        await self._ensure_index()
    
    async def _ensure_index(self):
        """Ensure alert index exists with proper mappings."""
        if not await self.es_client.indices.exists(index=self.index):
            await self.es_client.indices.create(
                index=self.index,
                mappings={
                    "properties": {
                        "title": {"type": "text"},
                        "description": {"type": "text"},
                        "severity": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "source_ip": {"type": "ip"},
                        "destination_ip": {"type": "ip"},
                        "affected_assets": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "assigned_to": {"type": "keyword"},
                        "acknowledged_at": {"type": "date"},
                        "resolved_at": {"type": "date"},
                        "closed_at": {"type": "date"}
                    }
                }
            )
    
    async def create_alert(self, alert: AlertCreate) -> Alert:
        """Create a new alert."""
        alert_dict = alert.model_dump()
        alert_dict["id"] = str(uuid.uuid4())
        
        await self.es_client.index(
            index=self.index,
            id=alert_dict["id"],
            document=alert_dict,
            refresh=True
        )
        
        return Alert(**alert_dict)
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Retrieve an alert by ID."""
        try:
            result = await self.es_client.get(
                index=self.index,
                id=alert_id
            )
            return Alert(**result["_source"])
        except NotFoundError:
            return None
    
    async def get_alerts(self, query: Dict[str, Any], limit: int = 50, skip: int = 0) -> List[Alert]:
        """Retrieve multiple alerts based on query."""
        result = await self.es_client.search(
            index=self.index,
            query=query,
            size=limit,
            from_=skip,
            sort=[{"timestamp": {"order": "desc"}}]
        )
        
        return [Alert(**hit["_source"]) for hit in result["hits"]["hits"]]
    
    async def update_alert(self, alert_id: str, alert_update: AlertUpdate) -> Optional[Alert]:
        """Update an existing alert."""
        try:
            alert = await self.get_alert(alert_id)
            if not alert:
                return None
            
            update_dict = alert_update.model_dump(exclude_unset=True)
            
            if "status" in update_dict:
                if update_dict["status"] == AlertStatus.RESOLVED:
                    update_dict["resolved_at"] = datetime.utcnow()
                elif update_dict["status"] == AlertStatus.CLOSED:
                    update_dict["closed_at"] = datetime.utcnow()
            
            await self.es_client.update(
                index=self.index,
                id=alert_id,
                doc=update_dict,
                refresh=True
            )
            
            alert_dict = alert.model_dump()
            alert_dict.update(update_dict)
            return Alert(**alert_dict)
            
        except NotFoundError:
            return None
    
    async def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert."""
        try:
            await self.es_client.delete(
                index=self.index,
                id=alert_id,
                refresh=True
            )
            return True
        except NotFoundError:
            return False
    
    async def acknowledge_alert(self, alert_id: str) -> Optional[Alert]:
        """Acknowledge an alert."""
        update = AlertUpdate(
            status=AlertStatus.ACKNOWLEDGED,
            acknowledged_at=datetime.utcnow()
        )
        return await self.update_alert(alert_id, update)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        result = await self.es_client.search(
            index=self.index,
            body={
                "size": 0,
                "aggs": {
                    "severity_stats": {
                        "terms": {"field": "severity"}
                    },
                    "status_stats": {
                        "terms": {"field": "status"}
                    },
                    "source_stats": {
                        "terms": {"field": "source"}
                    },
                    "recent_alerts": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "day"
                        }
                    }
                }
            }
        )
        
        return {
            "total_alerts": result["hits"]["total"]["value"],
            "by_severity": {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["severity_stats"]["buckets"]
            },
            "by_status": {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["status_stats"]["buckets"]
            },
            "by_source": {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["source_stats"]["buckets"]
            },
            "recent_trend": [
                {"date": bucket["key_as_string"], "count": bucket["doc_count"]}
                for bucket in result["aggregations"]["recent_alerts"]["buckets"]
            ]
        }