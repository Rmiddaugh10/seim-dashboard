# backend/scripts/setup_elasticsearch.py

import json
import asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import RequestError

templates = {
    "alerts": {
        "index_patterns": ["alerts-*"],
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "timestamp": { "type": "date" },
                    "title": { "type": "text" },
                    "description": { "type": "text" },
                    "severity": { "type": "keyword" },
                    "status": { "type": "keyword" },
                    "source": { "type": "keyword" },
                    "source_ip": { "type": "ip" },
                    "destination_ip": { "type": "ip" },
                    "affected_assets": { "type": "keyword" },
                    "tags": { "type": "keyword" },
                    "assigned_to": { "type": "keyword" },
                    "acknowledged_at": { "type": "date" },
                    "resolved_at": { "type": "date" },
                    "closed_at": { "type": "date" }
                }
            }
        }
    },
    "logs": {
        "index_patterns": ["logs-*"],
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "timestamp": { "type": "date" },
                    "message": { "type": "text" },
                    "level": { "type": "keyword" },
                    "source": { "type": "keyword" },
                    "host": { "type": "keyword" },
                    "metadata": { "type": "object" },
                    "tags": { "type": "keyword" },
                    "correlation_id": { "type": "keyword" },
                    "processed": { "type": "boolean" }
                }
            }
        }
    },
    "security-events": {
        "index_patterns": ["security-events-*"],
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "timestamp": { "type": "date" },
                    "event_type": { "type": "keyword" },
                    "severity": { "type": "keyword" },
                    "source_ip": { "type": "ip" },
                    "destination_ip": { "type": "ip" },
                    "description": { "type": "text" },
                    "raw_data": { "type": "object" },
                    "threat_score": { "type": "float" },
                    "indicators": { "type": "keyword" }
                }
            }
        }
    }
}

async def setup_elasticsearch():
    """Initialize Elasticsearch with index templates."""
    client = AsyncElasticsearch(['http://elasticsearch:9200'])
    
    try:
        # Wait for Elasticsearch to be ready
        await client.cluster.health(wait_for_status='yellow')
        
        # Create or update templates
        for name, template in templates.items():
            try:
                await client.indices.put_template(
                    name=f"{name}-template",
                    body=template
                )
                print(f"Successfully created template: {name}-template")
            except RequestError as e:
                print(f"Error creating template {name}: {e}")
        
        # Create initial indices if they don't exist
        indices = ['alerts-000001', 'logs-000001', 'security-events-000001']
        for index in indices:
            if not await client.indices.exists(index=index):
                await client.indices.create(index=index)
                print(f"Created initial index: {index}")
    
    except Exception as e:
        print(f"Error setting up Elasticsearch: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(setup_elasticsearch())