from uuid import uuid4

import pytest
import pytest_asyncio
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from app.models.user import UserRole
from app.schemas.request import RegisterUserRequest, UpdateUserRequest

fake = Faker()


@pytest.mark.asyncio
class TestUserEndpoints:
    @pytest_asyncio.fixture
    async def test_user(self, client: AsyncClient) -> dict:
        """Fixture to create a test user in the system."""
        user_data = {
            "email": fake.email(),
            "password": "Password@123",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "role": UserRole.USER,
            "activated": True,
        }
        response = await client.post("/api/v1/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        return response.json().get("content")

    async def test_get_all_users(self, client: AsyncClient, admin_auth_token: tuple[str, str]):
        """Test retrieving all users as an admin."""
        access_token, _ = admin_auth_token

        client.cookies.set(name="Access-Token", value=access_token)
        response = await client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_200_OK
        users = response.json().get("content")
        assert isinstance(users["items"], list)

    async def test_get_all_users_non_admin(self, client: AsyncClient, user_auth_token: tuple[str, str]):
        """Test retrieving all users as a non-admin user."""
        access_token, _ = user_auth_token

        client.cookies.set(name="Access-Token", value=access_token)
        response = await client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_all_users_unauthorized(self, client: AsyncClient):
        """Test retrieving all users without authentication."""
        response = await client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_user_by_id(self, client: AsyncClient, admin_auth_token: tuple[str, str], test_user: dict):
        """Test retrieving a user by their UUID as an admin."""
        access_token, _ = admin_auth_token
        user_uuid = test_user["uuid"]

        client.cookies.set(name="Access-Token", value=access_token)
        response = await client.get(f"/api/v1/users/{user_uuid}")

        assert response.status_code == status.HTTP_200_OK
        user_data = response.json().get("content")
        assert user_data["uuid"] == user_uuid

    async def test_register_new_user(self, client: AsyncClient):
        """Test registering a new user."""
        new_user = RegisterUserRequest(
            email="test@email.com",
            first_name="User",
            last_name="test",
            password="Password@123",
            role=UserRole.USER,
            activated=True,
        )
        response = await client.post("/api/v1/users/", json=new_user.model_dump())

        assert response.status_code == status.HTTP_201_CREATED
        user = response.json().get("content")
        assert user["email"] == "test@email.com"
        assert user["first_name"] == "User"
        assert user["last_name"] == "test"

    async def test_register_duplicate_user(self, client: AsyncClient):
        """Test registering a user with an email that already exists."""
        user1 = RegisterUserRequest(
            email="test@email.com",
            first_name="User",
            last_name="test",
            password="Password@123",
            role=UserRole.USER,
            activated=True,
        )
        response = await client.post("/api/v1/users/", json=user1.model_dump())
        assert response.status_code == status.HTTP_201_CREATED

        user2 = RegisterUserRequest(
            email="test@email.com",
            first_name="User",
            last_name="test",
            password="Password@123",
            role=UserRole.USER,
            activated=True,
        )
        response = await client.post("/api/v1/users/", json=user2.model_dump())
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_other_user_unauthorized(
        self, client: AsyncClient, user_auth_token: tuple[str, str], admin_auth_token: tuple[str, str]
    ):
        """Test updating another user without proper permissions."""
        access_token, _ = user_auth_token
        admin_token, _ = admin_auth_token

        new_user_data = RegisterUserRequest(
            email="another_test@email.com",
            first_name="Another",
            last_name="User",
            password="Password@123",
            role=UserRole.USER,
            activated=True,
        )
        client.cookies.set(name="Access-Token", value=admin_token)
        response = await client.post("/api/v1/users/", json=new_user_data.model_dump())
        other_user = response.json().get("content")

        assert response.status_code == status.HTTP_201_CREATED

        client.cookies.set(name="Access-Token", value=access_token)
        updated_user_data = UpdateUserRequest(
            email="updated_other_email@example.com",
            first_name="UpdatedOtherFirstName",
            last_name="UpdatedOtherLastName",
            password="UpdatedOther@Password123",
        )
        response = await client.put(f"/api/v1/users/{other_user['uuid']}", json=updated_user_data.model_dump())
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_non_existent_user(self, client: AsyncClient, user_auth_token: tuple[str, str]):
        """Test updating a non-existent user."""
        access_token, _ = user_auth_token
        non_existent_uuid = uuid4()
        updated_user_data = {
            "email": "non_existent@example.com",
            "first_name": "NonExistentFirstName",
            "last_name": "NonExistentLastName",
            "password": "NonExistent@Password123",
        }

        client.cookies.set(name="Access-Token", value=access_token)
        response = await client.put(f"/api/v1/users/{non_existent_uuid}", json=updated_user_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_other_user_unauthorized(
        self, client: AsyncClient, user_auth_token: tuple[str, str], admin_auth_token: tuple[str, str]
    ):
        """Test deleting another user without proper permissions."""
        access_token, _ = user_auth_token
        admin_token, _ = admin_auth_token

        new_user_data = RegisterUserRequest(
            email="delete_test@email.com",
            first_name="Delete",
            last_name="User",
            password="Password@123",
            role=UserRole.USER,
            activated=True,
        )
        client.cookies.set(name="Access-Token", value=admin_token)
        response = await client.post("/api/v1/users/", json=new_user_data.model_dump())
        other_user = response.json().get("content")

        assert response.status_code == status.HTTP_201_CREATED

        client.cookies.set(name="Access-Token", value=access_token)
        response = await client.delete(f"/api/v1/users/{other_user['uuid']}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_non_existent_user(self, client: AsyncClient, user_auth_token: tuple[str, str]):
        """Test deleting a non-existent user."""
        access_token, _ = user_auth_token
        non_existent_uuid = uuid4()

        client.cookies.set(name="Access-Token", value=access_token)
        response = await client.delete(f"/api/v1/users/{non_existent_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
