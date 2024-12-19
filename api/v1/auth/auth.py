from fastapi import APIRouter, Depends, Request, Response, status
from redis.asyncio import client

from app.controllers import AuthController
from app.models import User
from app.schemas.request import UserLoginRequest
from app.schemas.response import UserResponse
from core.factory import Factory
from core.fastapi.dependencies import (
    get_authenticated_user,
    get_cache,
    get_current_user,
    get_current_user_with_refresh_token,
)
from core.security import JWTHandler

auth_router = APIRouter()


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    login_user_request: UserLoginRequest,
    cache: client.Redis = Depends(get_cache),
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> None:
    """
    Login user.
    """
    tokens = await auth_controller.login(
        login_user_request=login_user_request,
        cache=cache,
    )

    response.set_cookie(
        key="Access-Token",
        value=tokens.access_token,
        secure=True,
        httponly=True,
        samesite="strict",
        expires=JWTHandler.token_expiration(tokens.access_token),
    )
    response.set_cookie(
        key="Refresh-Token",
        value=tokens.refresh_token,
        secure=True,
        httponly=True,
        samesite="strict",
        expires=JWTHandler.token_expiration(tokens.refresh_token),
    )
    response.headers["X-CSRF-TOKEN"] = tokens.csrf_token


@auth_router.post(
    "/refresh", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user_with_refresh_token)]
)
async def refresh_token(
    request: Request,
    response: Response,
    cache: client.Redis = Depends(get_cache),
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> None:
    """
    Retrieve new access and refresh token.
    """
    tokens = await auth_controller.refresh_token(
        old_refresh_token=request.cookies.get("Refresh-Token", ""),
        session_id=request.cookies.get("Session-Id", ""),
        cache=cache,
    )

    response.set_cookie(
        key="Access-Token",
        value=tokens.access_token,
        secure=True,
        httponly=True,
        samesite="strict",
        expires=JWTHandler.token_expiration(tokens.access_token),
    )
    response.set_cookie(
        key="Refresh-Token",
        value=tokens.refresh_token,
        secure=True,
        httponly=True,
        samesite="strict",
        expires=JWTHandler.token_expiration(tokens.refresh_token),
    )
    response.headers["X-CSRF-TOKEN"] = tokens.csrf_token


@auth_router.get("/me", status_code=status.HTTP_200_OK)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    """
    Retrieve current user information.
    """
    return UserResponse(
        uuid=user.uuid,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        activated=user.activated,
    )


@auth_router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_authenticated_user)])
async def logout(
    request: Request,
    response: Response,
    cache: client.Redis = Depends(get_cache),
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> None:
    """
    Logout user.
    """
    await auth_controller.logout(
        refresh_token=request.cookies.get("Refresh-Token", ""),
        cache=cache,
    )

    response.delete_cookie(key="Access-Token", secure=True, httponly=True, samesite="strict")
    response.delete_cookie(key="Refresh-Token", secure=True, httponly=True, samesite="strict")
    response.delete_cookie(key="Session-Id", secure=True, httponly=True, samesite="strict")
