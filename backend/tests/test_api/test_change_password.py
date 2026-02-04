import httpx
import pytest


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.asyncio
async def test_change_password(async_client: httpx.AsyncClient) -> None:
    data = {"username": "testname", "old_password": "testpassword", "new_password": "new_password"}
    response = await async_client.patch(url="/api/change-password", json=data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_change_password_with_incorrect_old_password(async_client: httpx.AsyncClient) -> None:
    data = {"username": "testname", "old_password": "incorrect_old_password", "new_password": "new_password"}
    response = await async_client.patch(url="/api/change-password", json=data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_password_with_unauthorized_username(async_client: httpx.AsyncClient) -> None:
    data = {"username": "unauthorized_username", "old_password": "testpassword", "new_password": "new_password"}
    response = await async_client.patch(url="/api/change-password", json=data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_password_with_unvalid_new_password(async_client: httpx.AsyncClient) -> None:
    data = {"username": "testname", "old_password": "testpassword", "new_password": "short"}
    response = await async_client.patch(url="/api/change-password", json=data)

    assert response.status_code == 422
