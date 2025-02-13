"""
Log ingestion and processing service.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from elasticsearch import AsyncElasticsearch
from ..models.log_entry import LogEntry, LogCreate, LogStatistics, LogAnalysis
import logging
import uuid
import json
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class LogIngestionService:
    def __init__(self):
        self.index = "logs"
        self.es_client = None
        self.batch_size = 1000
        self.processing_queue = asyncio.Queue()
        
    async def initialize(self, es_client: AsyncElasticsearch):
        """Initialize the service with elasticsearch client."""
        self.es_client = es_client
        await self._ensure_index()
        asyncio.create_task(self._process_queue())
    
    async def _ensure_index(self):
        """Ensure log index exists with proper mappings."""
        if not await self.es_client.indices.exists(index=self.index):
            await self.es_client.indices.create(
                index=self.index,
                mappings={
                    "properties": {
                        "message": {"type": "text"},
                        "level": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "host": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "metadata": {"type": "object"},
                        "tags": {"type": "keyword"},
                        "processed": {"type": "boolean"},
                        "correlation_id": {"type": "keyword"}
                    }
                }
            )
    
    async def _process_queue(self):
        """Background task to process logs."""
        while True:
            try:
                logs_to_process = []
                try:
                    while len(logs_to_process) < self.batch_size:
                        log = await asyncio.wait_for(
                            self.processing_queue.get(),
                            timeout=1.0
                        )
                        logs_to_process.append(log)
                except asyncio.TimeoutError:
                    if not logs_to_process:
                        continue

                # Process the batch of logs
                await self._process_logs_batch(logs_to_process)
                
                # Mark tasks as done
                for _ in range(len(logs_to_process)):
                    self.processing_queue.task_done()
                    
            except Exception as e:
                logger.error(f"Error processing log queue: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on error

    async def _process_logs_batch(self, logs: List[Dict]):
        """Process a batch of logs for patterns and correlations."""
        bulk_updates = []
        
        for log in logs:
            # Add processing logic here, for example:
            processed_data = {
                "processed": True,
                "metadata": {
                    "processed_at": datetime.utcnow().isoformat(),
                    "patterns_detected": self._detect_patterns(log),
                    "risk_score": self._calculate_risk_score(log)
                }
            }
            
            bulk_updates.extend([
                {"update": {"_index": self.index, "_id": log["id"]}},
                {"doc": processed_data}
            ])
        
        if bulk_updates:
            await self.es_client.bulk(operations=bulk_updates)

    def _detect_patterns(self, log: Dict) -> List[str]:
        """Detect patterns in log entry."""
        patterns = []
        message = log.get("message", "").lower()
        
        # Example pattern detection
        if "failed login" in message:
            patterns.append("authentication_failure")
        if "error" in message:
            patterns.append("error_occurrence")
        if "warning" in message:
            patterns.append("warning_flag")
            
        return patterns

    def _calculate_risk_score(self, log: Dict) -> float:
        """Calculate risk score for log entry."""
        score = 0.0
        
        # Level-based scoring
        level_scores = {
            "critical": 1.0,
            "error": 0.8,
            "warning": 0.5,
            "info": 0.2,
            "debug": 0.1
        }
        score += level_scores.get(log.get("level", "info").lower(), 0.1)
        
        # Content-based scoring
        message = log.get("message", "").lower()
        if any(term in message for term in ["attack", "breach", "vulnerability"]):
            score += 0.5
        if any(term in message for term in ["failed", "error", "exception"]):
            score += 0.3
            
        return min(1.0, score)

    async def get_logs(
        self,
        query: Dict[str, Any],
        limit: int = 50,
        skip: int = 0
    ) -> List[LogEntry]:
        """Retrieve logs based on query."""
        result = await self.es_client.search(
            index=self.index,
            query=query,
            size=limit,
            from_=skip,
            sort=[{"timestamp": {"order": "desc"}}]
        )
        
        return [LogEntry(**hit["_source"]) for hit in result["hits"]["hits"]]

    async def get_unique_sources(self) -> List[str]:
        """Get list of unique log sources."""
        result = await self.es_client.search(
            index=self.index,
            body={
                "size": 0,
                "aggs": {
                    "unique_sources": {
                        "terms": {
                            "field": "source",
                            "size": 1000
                        }
                    }
                }
            }
        )
        
        return [
            bucket["key"]
            for bucket in result["aggregations"]["unique_sources"]["buckets"]
        ]

    async def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> LogStatistics:
        """Get log statistics and aggregations."""
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
                    "by_level": {
                        "terms": {"field": "level"}
                    },
                    "by_source": {
                        "terms": {"field": "source"}
                    },
                    "by_processing": {
                        "terms": {"field": "processed"}
                    }
                }
            }
        )
        
        return LogStatistics(
            total_logs=result["hits"]["total"]["value"],
            logs_by_level={
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["by_level"]["buckets"]
            },
            logs_by_source={
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["by_source"]["buckets"]
            },
            time_range={
                "start": start_time or datetime.min,
                "end": end_time or datetime.utcnow()
            },
            processing_status={
                "processed": next(
                    (b["doc_count"] for b in result["aggregations"]["by_processing"]["buckets"] if b["key"]),
                    0
                ),
                "unprocessed": next(
                    (b["doc_count"] for b in result["aggregations"]["by_processing"]["buckets"] if not b["key"]),
                    0
                )
            }
        )

    async def analyze_logs(
        self,
        start_time: datetime,
        end_time: datetime,
        pattern: Optional[str] = None
    ) -> LogAnalysis:
        """Analyze logs for patterns and anomalies."""
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
        
        if pattern:
            query["bool"]["must"].append({
                "match": {"message": pattern}
            })

        result = await self.es_client.search(
            index=self.index,
            body={
                "size": 10000,  # Adjust based on your needs
                "query": query,
                "_source": ["message", "level", "timestamp", "source", "metadata"]
            }
        )

        logs = [hit["_source"] for hit in result["hits"]["hits"]]
        
        # Perform analysis
        patterns = self._analyze_patterns(logs)
        anomalies = self._detect_anomalies(logs)
        trends = self._analyze_trends(logs)
        
        return LogAnalysis(
            patterns=patterns,
            anomalies=anomalies,
            trends=trends,
            recommendations=self._generate_recommendations(patterns, anomalies, trends)
        )

    def _analyze_patterns(self, logs: List[Dict]) -> Dict[str, int]:
        """Analyze logs for common patterns."""
        patterns = defaultdict(int)
        
        for log in logs:
            message = log.get("message", "").lower()
            
            # Example pattern detection
            if "authentication" in message:
                patterns["authentication_related"] += 1
            if "failed" in message:
                patterns["failure_events"] += 1
            if "error" in message:
                patterns["error_events"] += 1
                
        return dict(patterns)

    def _detect_anomalies(self, logs: List[Dict]) -> List[Dict[str, Any]]:
        """Detect anomalies in logs."""
        anomalies = []
        
        # Example anomaly detection
        error_counts = defaultdict(int)
        timestamp_counts = defaultdict(int)
        
        for log in logs:
            error_counts[log.get("source", "")] += 1
            hour = log.get("timestamp", "")[:13]  # Group by hour
            timestamp_counts[hour] += 1
        
        # Detect unusual error rates
        avg_errors = sum(error_counts.values()) / len(error_counts) if error_counts else 0
        for source, count in error_counts.items():
            if count > avg_errors * 2:  # Simple threshold
                anomalies.append({
                    "type": "high_error_rate",
                    "source": source,
                    "count": count,
                    "average": avg_errors
                })
        
        return anomalies

    def _analyze_trends(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze trends in logs."""
        trends = {
            "error_trend": [],
            "activity_by_hour": defaultdict(int),
            "levels_distribution": defaultdict(int)
        }
        
        for log in logs:
            hour = datetime.fromisoformat(log["timestamp"]).strftime("%Y-%m-%d %H:00")
            trends["activity_by_hour"][hour] += 1
            trends["levels_distribution"][log.get("level")] += 1
        
        return {
            "activity_by_hour": dict(trends["activity_by_hour"]),
            "levels_distribution": dict(trends["levels_distribution"])
        }

    def _generate_recommendations(
        self,
        patterns: Dict[str, int],
        anomalies: List[Dict[str, Any]],
        trends: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Pattern-based recommendations
        if patterns.get("authentication_related", 0) > 100:
            recommendations.append(
                "High number of authentication events detected. Consider reviewing authentication policies."
            )
        
        # Anomaly-based recommendations
        for anomaly in anomalies:
            if anomaly["type"] == "high_error_rate":
                recommendations.append(
                    f"Unusually high error rate detected from {anomaly['source']}. "
                    f"Investigation recommended."
                )
        
        # Trend-based recommendations
        error_ratio = trends["levels_distribution"].get("error", 0) / sum(
            trends["levels_distribution"].values()
        ) if trends["levels_distribution"] else 0
        
        if error_ratio > 0.2:  # 20% threshold
            recommendations.append(
                "Error rate exceeds 20% of total logs. System health check recommended."
            )
        
        return recommendations

    async def delete_old_logs(self, older_than: datetime) -> int:
        """Delete logs older than specified date."""
        result = await self.es_client.delete_by_query(
            index=self.index,
            body={
                "query": {
                    "range": {
                        "timestamp": {
                            "lt": older_than.isoformat()
                        }
                    }
                }
            }
        )
        
        return result["deleted"]