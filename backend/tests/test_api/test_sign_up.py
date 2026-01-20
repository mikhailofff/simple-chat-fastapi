import httpx
import pytest


@pytest.mark.asyncio
async def test_sign_up(async_client: httpx.AsyncClient):
    data = {"username": "testname", "password": "testpassword"}
    response = await async_client.post(url="/api/sign-up", json=data)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] is not None
    assert data["username"] == "testname"
    assert data["hashed_password"] is not None


@pytest.mark.asyncio
async def test_sign_up_with_same_username(async_client: httpx.AsyncClient):
    data = {"username": "testname", "password": "testpassword"}
    response = await async_client.post(url="/api/sign-up", json=data)

    assert response.status_code == 409
