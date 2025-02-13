"""
Threat detection and analysis service.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from elasticsearch import AsyncElasticsearch
import logging
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class ThreatDetectionService:
    def __init__(self):
        self.index = "security_events"
        self.es_client = None
        self.threat_patterns = {
            "authentication_failure": r"failed\s+login|authentication\s+failure",
            "network_scan": r"port\s+scan|network\s+sweep",
            "malware_activity": r"malware|virus|trojan",
            "data_exfiltration": r"large\s+file\s+transfer|unusual\s+outbound",
            "privilege_escalation": r"sudo|privilege\s+elevation|permission\s+change"
        }
        
    async def initialize(self, es_client: AsyncElasticsearch):
        """Initialize the service with elasticsearch client."""
        self.es_client = es_client
        await self._ensure_index()
    
    async def _ensure_index(self):
        """Ensure security events index exists with proper mappings."""
        if not await self.es_client.indices.exists(index=self.index):
            await self.es_client.indices.create(
                index=self.index,
                mappings={
                    "properties": {
                        "timestamp": {"type": "date"},
                        "event_type": {"type": "keyword"},
                        "severity": {"type": "keyword"},
                        "source_ip": {"type": "ip"},
                        "destination_ip": {"type": "ip"},
                        "description": {"type": "text"},
                        "raw_data": {"type": "object"},
                        "threat_score": {"type": "float"},
                        "indicators": {"type": "keyword"}
                    }
                }
            )

    async def get_dashboard_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get aggregated metrics for dashboard display."""
        query = {
            "bool": {
                "must": [
                    {
                        "range": {
                            "timestamp": {
                                "gte": start_time.isoformat(),
                                "lte": end_time.isoformat()
                            }
                        }
                    }
                ]
            }
        }
        
        result = await self.es_client.search(
            index=self.index,
            body={
                "size": 0,
                "query": query,
                "aggs": {
                    "event_types": {
                        "terms": {"field": "event_type"}
                    },
                    "severity_levels": {
                        "terms": {"field": "severity"}
                    },
                    "timeline": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "hour"
                        }
                    },
                    "avg_threat_score": {
                        "avg": {"field": "threat_score"}
                    }
                }
            }
        )
        
        return {
            "event_distribution": {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["event_types"]["buckets"]
            },
            "severity_distribution": {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["severity_levels"]["buckets"]
            },
            "timeline": [
                {
                    "timestamp": bucket["key_as_string"],
                    "count": bucket["doc_count"]
                }
                for bucket in result["aggregations"]["timeline"]["buckets"]
            ],
            "average_threat_score": result["aggregations"]["avg_threat_score"]["value"]
        }

    async def get_threat_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of detected threats."""
        query = {"bool": {"must": [{"match_all": {}}]}}
        
        if start_time or end_time:
            query["bool"]["must"].append({
                "range": {
                    "timestamp": {
                        **({"gte": start_time.isoformat()} if start_time else {}),
                        **({"lte": end_time.isoformat()} if end_time else {})
                    }
                }
            })
        
        result = await self.es_client.search(
            index=self.index,
            body={
                "size": 0,
                "query": query,
                "aggs": {
                    "threat_types": {
                        "terms": {"field": "event_type"}
                    },
                    "top_sources": {
                        "terms": {"field": "source_ip"}
                    },
                    "severity_levels": {
                        "terms": {"field": "severity"}
                    }
                }
            }
        )
        
        return {
            "total_threats": result["hits"]["total"]["value"],
            "by_type": {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["threat_types"]["buckets"]
            },
            "top_sources": [
                {"ip": bucket["key"], "count": bucket["doc_count"]}
                for bucket in result["aggregations"]["top_sources"]["buckets"]
            ],
            "severity_distribution": {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["severity_levels"]["buckets"]
            }
        }

    async def calculate_security_score(self) -> Dict[str, Any]:
        """Calculate overall security score based on various metrics."""
        result = await self.es_client.search(
            index=self.index,
            body={
                "size": 0,
                "aggs": {
                    "avg_threat_score": {
                        "avg": {"field": "threat_score"}
                    },
                    "severity_distribution": {
                        "terms": {"field": "severity"}
                    },
                    "recent_threats": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "day"
                        }
                    }
                }
            }
        )
        
        # Calculate weighted score
        severity_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        
        severity_counts = {
            bucket["key"]: bucket["doc_count"]
            for bucket in result["aggregations"]["severity_distribution"]["buckets"]
        }
        
        total_events = sum(severity_counts.values())
        weighted_score = sum(
            count * severity_weights.get(severity, 0)
            for severity, count in severity_counts.items()
        ) / (total_events if total_events > 0 else 1)
        
        return {
            "overall_score": 100 * (1 - weighted_score),
            "threat_score": result["aggregations"]["avg_threat_score"]["value"],
            "severity_distribution": severity_counts,
            "trend": [
                {
                    "date": bucket["key_as_string"],
                    "count": bucket["doc_count"]
                }
                for bucket in result["aggregations"]["recent_threats"]["buckets"]
            ]
        }

    async def detect_anomalies(
        self,
        sensitivity: float = 0.75,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Detect security anomalies in events."""
        query = {"bool": {"must": [{"match_all": {}}]}}
        
        if start_time or end_time:
            query["bool"]["must"].append({
                "range": {
                    "timestamp": {
                        **({"gte": start_time.isoformat()} if start_time else {}),
                        **({"lte": end_time.isoformat()} if end_time else {})
                    }
                }
            })
        
        result = await self.es_client.search(
            index=self.index,
            body={
                "size": 1000,
                "query": query,
                "sort": [{"timestamp": {"order": "desc"}}]
            }
        )
        
        events = [hit["_source"] for hit in result["hits"]["hits"]]
        anomalies = []
        
        # Simple anomaly detection based on frequency and patterns
        event_counts = defaultdict(int)
        ip_counts = defaultdict(int)
        
        for event in events:
            event_type = event.get("event_type", "unknown")
            source_ip = event.get("source_ip")
            
            event_counts[event_type] += 1
            if source_ip:
                ip_counts[source_ip] += 1
        
        # Detect unusual patterns
        avg_events = sum(event_counts.values()) / len(event_counts) if event_counts else 0
        threshold = avg_events * sensitivity
        
        for event_type, count in event_counts.items():
            if count > threshold:
                anomalies.append({
                    "type": "frequency_anomaly",
                    "event_type": event_type,
                    "count": count,
                    "threshold": threshold,
                    "description": f"Unusually high frequency of {event_type} events"
                })
        
        # Detect suspicious IPs
        avg_ip_events = sum(ip_counts.values()) / len(ip_counts) if ip_counts else 0
        ip_threshold = avg_ip_events * sensitivity
        
        for ip, count in ip_counts.items():
            if count > ip_threshold:
                anomalies.append({
                    "type": "source_anomaly",
                    "source_ip": ip,
                    "count": count,
                    "threshold": ip_threshold,
                    "description": f"Suspicious activity from IP {ip}"
                })
        
        return anomalies