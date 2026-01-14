import pytest
import httpx
from datetime import datetime

from ..conftest import create_expired_token

from src.schemas.config import settings


@pytest.mark.order(after="tests/test_api/test_token.py::test_token_with_unauthorized_username")
@pytest.mark.asyncio
async def test_messages_empty(async_client: httpx.AsyncClient):
    access_token = async_client.cookies.get("access_token")
    response = await async_client.get(
        "/api/messages",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["messages"] == []


@pytest.mark.order(after="test_messages_empty")
@pytest.mark.asyncio
async def test_messages_as_unauthorized(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/messages")

    assert response.status_code == 401


@pytest.mark.order(after="test_messages_as_unauthorized")
@pytest.mark.asyncio
async def test_messages_with_invalid_token(async_client: httpx.AsyncClient):
    access_token = "invalid_token"
    response = await async_client.get(
        "/api/messages",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_messages_with_invalid_token")
@pytest.mark.asyncio
async def test_messages_with_expired_token(async_client: httpx.AsyncClient):
    expired_token = await create_expired_token({"sub": "testname"}, settings.SECRET_KEY)

    response = await async_client.get(
        "/api/messages",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401


@pytest.mark.order(after="tests/test_api/test_send_message.py::test_send_message_with_expired_token")
@pytest.mark.asyncio
async def test_messages_not_empty(async_client: httpx.AsyncClient):
    access_token = async_client.cookies.get("access_token")
    response = await async_client.get(
        "/api/messages",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["messages"] == [
        {
            "id": 1,
            "content": "Hello world!",
            "created_at": datetime(2026, 1, 1, 0, 0, 0).isoformat(),
            "updated_at": None,
            "created_by": "testname"
        }
    ]