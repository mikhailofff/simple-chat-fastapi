import httpx
import pytest

from src.schemas.config import settings

from ..conftest import create_expired_token


@pytest.mark.order(after="tests/test_api/test_update_message.py::test_update_message_with_expired_token")
@pytest.mark.asyncio
async def test_delete_message_as_unauthorized(async_client: httpx.AsyncClient):
    message_request = {"id": "1"}

    response = await async_client.delete("/api/delete-message", params=message_request)

    assert response.status_code == 401


@pytest.mark.order(after="test_delete_message_as_unauthorized")
@pytest.mark.asyncio
async def test_delete_message_with_invalid_token(async_client: httpx.AsyncClient):
    access_token = "invalid_token"
    message_request = {"id": "1"}

    response = await async_client.delete(
        "/api/delete-message", params=message_request, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_delete_message_with_invalid_token")
@pytest.mark.asyncio
async def test_delete_message_with_expired_token(async_client: httpx.AsyncClient):
    expired_token = create_expired_token({"sub": "testname"}, settings.SECRET_KEY)
    message_request = {"id": "1"}

    response = await async_client.delete(
        "/api/delete-message", params=message_request, headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_delete_message_with_expired_token")
@pytest.mark.asyncio
async def test_delete_message(async_client: httpx.AsyncClient):
    access_token = async_client.cookies.get("access_token")
    message_request = {"id": "1"}

    response = await async_client.delete(
        "/api/delete-message", params=message_request, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.order(after="test_delete_message")
@pytest.mark.asyncio
async def test_delete_unknown_message(async_client: httpx.AsyncClient):
    access_token = async_client.cookies.get("access_token")
    message_request = {"id": "1"}

    response = await async_client.delete(
        "/api/delete-message", params=message_request, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 400
