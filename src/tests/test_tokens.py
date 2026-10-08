import pytest
from fastapi import status

API_TOKEN_URL = "/api/v1/token"


@pytest.mark.asyncio()
async def test_get_token(async_client, seller):

    response = await async_client.post(
        f"{API_TOKEN_URL}/",
        json={
            "email": seller["email"],
            "password": "123456",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio()
async def test_get_token_with_wrong_password(async_client, seller):

    response = await async_client.post(
        f"{API_TOKEN_URL}/",
        json={
            "email": seller["email"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED



@pytest.mark.asyncio()
async def test_get_token_with_wrong_email(async_client):

    response = await async_client.post(
        f"{API_TOKEN_URL}/",
        json={
            "email": "unknown@test.com",
            "password": "123456",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED