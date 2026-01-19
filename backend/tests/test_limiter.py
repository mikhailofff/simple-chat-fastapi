import pytest
import httpx

from src.dependencies import limiter


@pytest.mark.asyncio
async def test_limiter(async_client: httpx.AsyncClient):
    response = None
    for _ in range(limiter.times):
        response = await async_client.get("/api/messages")
    
    assert response is not None
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_limiter_too_many_requests(async_client: httpx.AsyncClient):
    response = None
    for _ in range(limiter.times + 1):
        response = await async_client.get("/api/messages")
    
    assert response is not None
    assert response.status_code == 429