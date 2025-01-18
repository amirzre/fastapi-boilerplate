from .auth import UserLoginRequest
from .post import CreatePostRequest, UpdatePostRequest
from .user import RegisterUserRequest, UpdateUserRequest

__all__ = [
    "RegisterUserRequest",
    "UpdateUserRequest",
    "UserLoginRequest",
    "CreatePostRequest",
    "UpdatePostRequest",
]
