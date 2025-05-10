import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pydantic import UUID4

from app.models import PostStatus, UserRole
from app.schemas.request import CreatePostRequest, RegisterUserRequest, UpdatePostRequest
from app.schemas.response.user import UserResponse

fake = Faker()


@pytest.mark.asyncio
class TestPostEndpoints:
    """
    Test cases for the post endpoints supporting CRUD operations.

    This class demonstrates tests both with admin and normal users.
    Some tests expect failures when a user without sufficient permissions
    attempts to update or delete a post not created by them.
    """

    async def _create_user(self, client: AsyncClient, role: UserRole) -> UserResponse:
        """
        Helper method to create a new user using the API.

        :param client: The AsyncClient instance.
        :param role: Role of the user (UserRole.ADMIN or UserRole.USER).
        :return: The user JSON response (expects a field "uuid").
        """
        user_data = RegisterUserRequest(
            email=fake.email(),
            password="Password@123",
            first_name=fake.file_name(),
            last_name=fake.last_name(),
            role=role,
            activated=True,
        ).model_dump()

        response = await client.post("/api/v1/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED

        user = response.json().get("content")

        assert "uuid" in user

        return UserResponse(
            uuid=user["uuid"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            role=user["role"],
            activated=user["activated"],
        )

    async def _create_post(
        self,
        client: AsyncClient,
        token_fixture: str,
        user_id: UUID4,
        title: str = "Test Post Title",
    ) -> dict:
        """
        Helper method to create a new post for a specified user.

        :param client: The AsyncClient instance already authenticated.
        :param token_fixture: The authentication tokens tuple (not used directly here since the cookie is set by fixture)
        :param user_id: The UUID of the user that owns the post.
        :param title: Post title.
        :return: The created post as a dict.
        """
        post_request = CreatePostRequest(
            user_id=user_id,
            title=title,
            content="Test post content",
            status=PostStatus.DRAFT,
        )

        post_payload = {
            "user_id": str(post_request.user_id),
            "title": post_request.title,
            "content": post_request.content,
            "status": post_request.status.value,
        }

        client.cookies.set(name="Access-Token", value=token_fixture)

        response = await client.post("/api/v1/posts/", json=post_payload)

        assert response.status_code == status.HTTP_201_CREATED

        post = response.json().get("content")
        return post

    async def test_create_post_as_admin(self, client: AsyncClient, admin_auth_token: tuple[str, str]):
        """
        Test that an admin user can successfully create a post.
        """
        access_token, _ = admin_auth_token
        user = await self._create_user(client, role=UserRole.ADMIN)
        post = await self._create_post(client, access_token, user_id=user.uuid, title="Admin Post")

        assert "uuid" in post
        assert post["title"] == "Admin Post"

    async def test_create_post_as_normal_user(self, client: AsyncClient, user_auth_token: tuple[str, str]):
        """
        Test that a normal authenticated user can successfully create a post.
        """
        access_token, _ = user_auth_token
        user = await self._create_user(client, role=UserRole.USER)
        post = await self._create_post(client, access_token, user_id=user.uuid, title="User Post")

        assert "uuid" in post
        assert post["title"] == "User Post"

    async def test_create_post_unauthenticated(self, client: AsyncClient):
        """
        Test that unauthenticated requests to create a post fail.
        Remove any authentication cookie by not using admin_auth_token or user_auth_token.
        """
        user = await self._create_user(client, role=UserRole.USER)
        post_request = CreatePostRequest(
            user_id=user.uuid,
            title="Unauthorized Post",
            content="Test post content",
            status=PostStatus.DRAFT,
        )
        post_payload = {
            "user_id": str(post_request.user_id),
            "title": post_request.title,
            "content": post_request.content,
            "status": post_request.status.value,
        }

        response = await client.post("/api/v1/posts/", json=post_payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_post(self, client: AsyncClient, admin_auth_token: tuple[str, str]):
        """
        Test retrieving an individual post by its UUID.
        """
        access_token, _ = admin_auth_token
        user = await self._create_user(client, role=UserRole.USER)
        created_post = await self._create_post(client, access_token, user_id=user.uuid, title="Get Post Test")
        post_uuid = created_post["uuid"]

        response = await client.get(f"/api/v1/posts/{post_uuid}")

        assert response.status_code == status.HTTP_200_OK

        fetched_post = response.json().get("content")

        assert fetched_post["uuid"] == post_uuid
        assert fetched_post["title"] == "Get Post Test"

    async def test_update_post_by_non_owner(
        self, client: AsyncClient, admin_auth_token: tuple[str, str], user_auth_token: tuple[str, str]
    ):
        """
        Test that a user that is not the owner of the post is not allowed to update it.
        In this example, we create a post with the admin, then attempt to update it with a normal user.
        """
        admin_access_token, _ = admin_auth_token
        user_access_token, _ = user_auth_token
        admin_user = await self._create_user(client, role=UserRole.ADMIN)
        created_post = await self._create_post(
            client, admin_access_token, user_id=admin_user.uuid, title="Admin Post for Update"
        )
        post_uuid = created_post["uuid"]

        update_payload = UpdatePostRequest(
            title="Updated Title",
            content="Updated Content",
            status=PostStatus.ARCHIVED,
        ).model_dump()

        client.cookies.set(name="Access-Token", value=user_access_token)
        unauthenticated_response = await client.put(f"/api/v1/posts/{post_uuid}", json=update_payload)

        assert unauthenticated_response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_post_by_non_owner(
        self, client: AsyncClient, admin_auth_token: tuple[str, str], user_auth_token: tuple[str, str]
    ):
        """
        Test that a user that is not the owner cannot delete the post.
        In this example, an admin creates the post and then a normal user attempts deletion.
        """
        admin_access_token, _ = admin_auth_token
        user_access_token, _ = user_auth_token
        admin_user = await self._create_user(client, role=UserRole.ADMIN)
        created_post = await self._create_post(
            client, admin_access_token, user_id=admin_user.uuid, title="Post to Delete by Non-Owner"
        )
        post_uuid = created_post["uuid"]

        client.cookies.set(name="Access-Token", value=user_access_token)
        response = await client.delete(f"/api/v1/posts/{post_uuid}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
