import httpx
import pytest


@pytest.mark.asyncio
async def test_token(async_client: httpx.AsyncClient) -> None:
    form_data = {"username": "testname", "password": "testpassword"}
    response = await async_client.post(url="/api/token", data=form_data)

    assert response.status_code == 200
    data = response.json()

    assert data["access_token"] is not None
    async_client.cookies.set("access_token", data["access_token"])
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_token_with_incorrect_password(async_client: httpx.AsyncClient) -> None:
    form_data = {"username": "testname", "password": "incorrect_password"}
    response = await async_client.post(url="/api/token", data=form_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_with_unauthorized_username(async_client: httpx.AsyncClient) -> None:
    form_data = {"username": "unauthorized_username", "password": "incorrect_password"}
    response = await async_client.post(url="/api/token", data=form_data)

    assert response.status_code == 401
