from typing import Any, Generator

import pytest
import pytest_asyncio
from faker import Faker
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.models import UserRole
from app.schemas.request import RegisterUserRequest
from core.factory.factory import get_session
from core.server import create_app

fake = Faker()


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a new FastAPI app.
    """
    app = create_app()

    yield app


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI, db_session) -> AsyncClient:
    """
    Provides an HTTP client for making requests to the FastAPI app.
    Overrides the session dependency to use the test database.
    """

    async def _get_session():
        return db_session

    app.dependency_overrides[get_session] = _get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def register_admin_user(client: AsyncClient) -> dict:
    """
    Registers an admin user with the application.
    """
    admin_data = RegisterUserRequest(
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        password=fake.password(),
        role=UserRole.ADMIN,
        activated=True,
    )
    await client.post("/api/v1/users/", json=admin_data.model_dump())
    return {"email": admin_data.email, "password": admin_data.password}


@pytest_asyncio.fixture(scope="function")
async def register_normal_user(client: AsyncClient) -> dict:
    """
    Registers a normal user with the application.
    """
    normal_user_data = RegisterUserRequest(
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        password=fake.password(),
        role=UserRole.USER,
        activated=True,
    )
    await client.post("/api/v1/users/", json=normal_user_data.model_dump())
    return {"email": normal_user_data.email, "password": normal_user_data.password}


@pytest_asyncio.fixture(scope="function")
async def admin_auth_token(client: AsyncClient, register_admin_user: dict) -> tuple[str | None, str | None]:
    """
    Logs in the registered admin user and retrieves authentication tokens.
    """
    login_response = await client.post(
        "/api/v1/auth/login", json={"email": register_admin_user["email"], "password": register_admin_user["password"]}
    )
    client.cookies.update(login_response.cookies)
    access_token = login_response.cookies.get("Access-Token")
    refresh_token = login_response.cookies.get("Refresh-Token")
    return access_token, refresh_token


@pytest_asyncio.fixture(scope="function")
async def user_auth_token(client: AsyncClient, register_normal_user: dict) -> tuple[str | None, str | None]:
    """
    Logs in the registered normal user and retrieves authentication tokens.
    """
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": register_normal_user["email"], "password": register_normal_user["password"]},
    )
    access_token = login_response.cookies.get("Access-Token")
    refresh_token = login_response.cookies.get("Refresh-Token")
    return access_token, refresh_token