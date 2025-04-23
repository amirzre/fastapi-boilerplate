from typing import Optional

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials

from core.exceptions import UnauthorizedException
from core.i18n import translate as _
from core.security import JWTHandler


class AuthenticationHandler:
    """
    Handles user authentication by managing and validating JWT tokens.

    This class abstracts the process of:
    - Retrieving tokens from cookies,
    - Validating the Bearer scheme,
    - Decoding JWT payloads to extract user-specific information.
    """

    def __init__(self, request: Request):
        """
        Initialize the authentication handler with the current HTTP request.

        Args:
            request (Request): The current request object.
        """
        self.request = request

    async def _get_token(self, token_type: str) -> str:
        """
        Retrieve a JWT token from the request cookies.

        Args:
            token_type (str): The type of token to retrieve (e.g., "Access", "Refresh").

        Raises:
            UnauthorizedException: If the token is not provided in the cookies.

        Returns:
            str: The JWT token as a string.
        """
        token = self.request.cookies.get(f"{token_type}-Token")
        if not token:
            raise UnauthorizedException(message=_(f"{token_type}-Token is not provided."))
        return token

    async def _decode_token(self, token: str, key: str) -> str:
        """
        Decode a JWT token and extract a value by key from its payload.

        Args:
            token (str): The JWT token to decode.
            key (str): The key to retrieve from the decoded payload.

        Raises:
            UnauthorizedException: If the token is invalid or does not contain the expected key.

        Returns:
            str: The value associated with the specified key in the token.
        """
        decoded_token = JWTHandler.decode(token=token)
        user_uuid = decoded_token.get(key)
        if not user_uuid:
            raise UnauthorizedException(message=_("Invalid token."))
        return user_uuid

    async def _validate_token(self, token: str, credentials: HTTPAuthorizationCredentials, token_type: str) -> None:
        """
        Validate that the provided Bearer token matches the one from the cookies.

        Args:
            token (str): The token retrieved from the cookies.
            credentials (HTTPAuthorizationCredentials): The credentials provided in the Authorization header.
            token_type (str): The type of token for error context.

        Raises:
            UnauthorizedException: If the credentials do not match or the scheme is not Bearer.
        """
        if credentials.scheme != "Bearer" or credentials.credentials != token:
            raise UnauthorizedException(message=_("Invalid token."))

    async def authenticate_user(
        self, token_type: str, key: str, credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> str:
        """
        Authenticate the user by validating and decoding a JWT token.

        This method performs:
        - Token retrieval from cookies,
        - Optional validation against Bearer credentials,
        - Decoding to extract the user identifier or claim.

        Args:
            token_type (str): The type of token ("Access", "Refresh", etc.).
            key (str): The claim key to extract from the decoded token.
            credentials (Optional[HTTPAuthorizationCredentials]): Optional credentials to validate against the token.

        Raises:
            UnauthorizedException: If authentication fails at any step.

        Returns:
            str: The value associated with the provided key in the JWT payload.
        """
        token = await self._get_token(token_type)

        if credentials:
            await self._validate_token(token, credentials, token_type)

        return await self._decode_token(token, key)
