from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials

from core.exceptions import UnauthorizedException
from core.i18n import translate as _
from core.security import JWTHandler


class AuthenticationHandler:
    def __init__(self, request: Request):
        self.request = request

    async def _get_token(self, token_type: str) -> str:
        token = self.request.cookies.get(f"{token_type}-Token")
        if not token:
            raise UnauthorizedException(message=_(f"{token_type}-Token is not provided."))
        return token

    async def _decode_token(self, token: str, key: str) -> str:
        decoded_token = JWTHandler.decode(token=token)
        user_uuid = decoded_token.get(key)
        if not user_uuid:
            raise UnauthorizedException(message=_("Invalid token."))
        return user_uuid

    async def _validate_token(self, token: str, credentials: HTTPAuthorizationCredentials, token_type: str) -> None:
        if credentials.scheme != "Bearer" or credentials.credentials != token:
            raise UnauthorizedException(message=_("Invalid token."))

    async def authenticate_user(
        self, token_type: str, key: str, credentials: HTTPAuthorizationCredentials = None
    ) -> str:
        token = await self._get_token(token_type)

        if credentials:
            await self._validate_token(token, credentials, token_type)

        return await self._decode_token(token, key)
