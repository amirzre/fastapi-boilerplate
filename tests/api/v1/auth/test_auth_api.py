import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.request import UserLoginRequest


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_login_success(self, client: AsyncClient, register_normal_user: dict):
        """Test that user can login successfully."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": register_normal_user.get("email"), "password": register_normal_user.get("password")},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "Access-Token" in response.cookies
        assert "Refresh-Token" in response.cookies

    async def test_login_failure(self, client: AsyncClient):
        """Test user with wrong credentials can not login."""
        login_request = UserLoginRequest(email="user@example.com", password="Wrong@password123")
        response = await client.post("/api/v1/auth/login", json=login_request.model_dump())

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_refresh_success(self, client: AsyncClient, user_auth_token: tuple[str, str]):
        """Test that user can get new access and refresh token."""
        _, refresh_token = user_auth_token

        client.cookies.set(name="Refresh-Token", value=refresh_token)
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == status.HTTP_200_OK
        assert "Access-Token" in response.cookies
        assert "Refresh-Token" in response.cookies

    async def test_refresh_failure(self, client: AsyncClient):
        """Test that user refresh token is invalid can not get new tokens."""
        client.cookies.set(name="Refresh-Token", value="invalidtoken")
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_me_success(self, client: AsyncClient, user_auth_token: tuple[str, str]):
        """Test get current user information."""
        access_token, _ = user_auth_token
        client.cookies.set(name="Access-Token", value=access_token)
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_200_OK
        user_data = response.json().get("content")
        assert "email" in user_data

    async def test_me_unauthorized(self, client: AsyncClient):
        """Test that unauthorized user can not get information."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_logout_success(self, client: AsyncClient, user_auth_token: tuple[str, str]):
        """Test users can logout successfully."""
        access_token, refresh_token = user_auth_token

        client.cookies.set(name="Access-Token", value=access_token)
        client.cookies.set(name="Refresh-Token", value=refresh_token)
        response = await client.delete("/api/v1/auth/logout", cookies={})

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert "Access-Token" not in response.cookies
        assert "Refresh-Token" not in response.cookies

    async def test_logout_unauthorized(self, client: AsyncClient):
        """Test unauthorized users can not logout."""
        response = await client.delete("/api/v1/auth/logout")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
