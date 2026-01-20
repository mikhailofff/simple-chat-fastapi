from datetime import datetime

import httpx
import pytest

from src.schemas.config import settings

from ..conftest import create_expired_token


@pytest.mark.order(after="tests/test_api/test_token.py::test_token_with_unauthorized_username")
@pytest.mark.asyncio
async def test_send_message(async_client: httpx.AsyncClient):
    access_token = async_client.cookies.get("access_token")
    message_request = {
        "content": "Hello world!",
        "created_at": datetime(2026, 1, 1, 0, 0, 0).isoformat(),
        "updated_at": None,
        "created_by": "testname",
    }
    response = await async_client.post(
        "/api/send-message", json=message_request, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1


@pytest.mark.order(after="test_send_message")
@pytest.mark.asyncio
async def test_send_message_as_unauthorized(async_client: httpx.AsyncClient):
    message_request = {
        "content": "Hello world!",
        "created_at": datetime(2026, 1, 1, 0, 0, 0).isoformat(),
        "updated_at": None,
        "created_by": "testname",
    }
    response = await async_client.post("/api/send-message", json=message_request)

    assert response.status_code == 401


@pytest.mark.order(after="test_send_message_as_unauthorized")
@pytest.mark.asyncio
async def test_send_message_with_invalid_token(async_client: httpx.AsyncClient):
    access_token = "invalid_token"
    message_request = {
        "content": "Hello world!",
        "created_at": datetime(2026, 1, 1, 0, 0, 0).isoformat(),
        "updated_at": None,
        "created_by": "testname",
    }
    response = await async_client.post(
        "/api/send-message", json=message_request, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_send_message_with_invalid_token")
@pytest.mark.asyncio
async def test_send_message_with_expired_token(async_client: httpx.AsyncClient):
    expired_token = create_expired_token({"sub": "testname"}, settings.SECRET_KEY)

    message_request = {
        "content": "Hello world!",
        "created_at": datetime(2026, 1, 1, 0, 0, 0).isoformat(),
        "updated_at": None,
        "created_by": "testname",
    }
    response = await async_client.post(
        "/api/send-message", json=message_request, headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
