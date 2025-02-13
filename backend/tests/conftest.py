# tests/conftest.py
import pytest
import asyncio
from elasticsearch import AsyncElasticsearch
from app.core.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def es_client():
    """Create a test elasticsearch client."""
    client = AsyncElasticsearch(
        [f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"]
    )
    yield client
    await client.close()