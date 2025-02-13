"""
Main FastAPI application instance and configuration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from .core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Elasticsearch client
es_client = Elasticsearch(
    [f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"],
    basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD) 
    if settings.ELASTICSEARCH_USERNAME else None
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        if not es_client.ping():
            raise Exception("Elasticsearch connection failed")
        logger.info("Successfully connected to Elasticsearch")
        
        # Create necessary indices if they don't exist
        if not es_client.indices.exists(index="logs"):
            es_client.indices.create(
                index="logs",
                mappings={
                    "properties": {
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "message": {"type": "text"},
                        "host": {"type": "keyword"}
                    }
                }
            )
            logger.info("Created logs index")
            
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        es_client.close()
        logger.info("Closed Elasticsearch connection")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# Import and include API routers
from .api.endpoints import alerts, logs, metrics

app.include_router(
    alerts.router,
    prefix=f"{settings.API_V1_STR}/alerts",
    tags=["alerts"]
)

app.include_router(
    logs.router,
    prefix=f"{settings.API_V1_STR}/logs",
    tags=["logs"]
)

app.include_router(
    metrics.router,
    prefix=f"{settings.API_V1_STR}/metrics",
    tags=["metrics"]
)