import httpx
import pytest

from src.schemas.config import settings

from ..conftest import create_expired_token


@pytest.mark.order(after="tests/test_api/test_token.py::test_token_with_unauthorized_username")
@pytest.mark.asyncio
async def test_refresh(async_client: httpx.AsyncClient) -> None:
    response = await async_client.post(
        "/api/refresh", headers={"Cookie": f"refresh_token={async_client.cookies.get("refresh_token")}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"


@pytest.mark.order(after="test_refresh")
@pytest.mark.asyncio
async def test_refresh_with_invalid_token(async_client: httpx.AsyncClient) -> None:
    response = await async_client.post("/api/refresh", headers={"Cookie": "refresh_token=invalid_token"})

    assert response.status_code == 401


@pytest.mark.order(after="test_refresh_with_invalid_token")
@pytest.mark.asyncio
async def test_refresh_without_token(async_client: httpx.AsyncClient) -> None:
    response = await async_client.post("/api/refresh")

    assert response.status_code == 401


@pytest.mark.order(after="test_refresh_without_token")
@pytest.mark.asyncio
async def test_refresh_with_expired_token(async_client: httpx.AsyncClient) -> None:
    expired_token = create_expired_token({"sub": "testname"}, settings.SECRET_KEY)

    response = await async_client.post("/api/refresh", headers={"Cookie": f"refresh_token={expired_token}"})

    assert response.status_code == 401
