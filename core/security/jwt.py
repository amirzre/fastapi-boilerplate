from datetime import datetime, timedelta, timezone

import jwt
from fastapi import status

from core.config import config
from core.exceptions import CustomException
from core.i18n import translate as _


class JWTDecodeError(CustomException):
    """Exception raised when JWT token decoding fails due to invalid token."""

    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = _("Invalid token.")


class JWTExpiredError(CustomException):
    """Exception raised when a JWT token has expired."""

    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = _("Token expired.")


class JWTHandler:
    """
    A handler class for encoding and decoding JWT access and refresh tokens.

    Attributes:
        secret_key (str): Secret key used for encoding and decoding tokens.
        algorithm (str): Algorithm used to sign the JWT.
        access_token_expire (int): Expiration time in minutes for access tokens.
        refresh_token_expire (int): Expiration time in minutes for refresh tokens.
    """

    secret_key = config.SECRET_KEY
    algorithm = config.JWT_ALGORITHM
    access_token_expire = config.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire = config.REFRESH_TOKEN_EXPIRE_MINUTES

    @staticmethod
    def encode(payload: dict) -> str:
        """
        Generates a JWT access token.

        Args:
            payload (dict): The payload to encode into the token.

        Returns:
            str: A JWT access token.
        """
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTHandler.access_token_expire)
        payload.update({"exp": expire})
        return jwt.encode(
            payload=payload,
            key=JWTHandler.secret_key,
            algorithm=JWTHandler.algorithm,
        )

    @staticmethod
    def encode_refresh_token(payload: dict) -> str:
        """
        Generates a JWT refresh token.

        Args:
            payload (dict): The payload to encode into the refresh token.

        Returns:
            str: A JWT refresh token.
        """
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTHandler.refresh_token_expire)
        payload.update({"exp": expire})
        return jwt.encode(
            payload=payload,
            key=JWTHandler.secret_key,
            algorithm=JWTHandler.algorithm,
        )

    @staticmethod
    def decode(token: str) -> dict:
        """
        Decodes and verifies a JWT token.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded payload.

        Raises:
            JWTDecodeError: If the token is invalid.
            JWTExpiredError: If the token is expired.
        """
        try:
            return jwt.decode(
                token,
                key=JWTHandler.secret_key,
                algorithms=[JWTHandler.algorithm],
            )
        except jwt.exceptions.DecodeError as exception:
            raise JWTDecodeError() from exception
        except jwt.exceptions.ExpiredSignatureError as exception:
            raise JWTExpiredError() from exception

    @staticmethod
    def decode_expired(token: str) -> dict:
        """
        Decodes a JWT token without verifying its expiration.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded payload.

        Raises:
            JWTDecodeError: If the token is invalid.
        """
        try:
            return jwt.decode(
                token,
                key=JWTHandler.secret_key,
                algorithms=[JWTHandler.algorithm],
                options={"verify_exp": False},
            )
        except jwt.exceptions.DecodeError as exception:
            raise JWTDecodeError() from exception

    @staticmethod
    def token_expiration(token: str) -> datetime | None:
        """
        Extracts the expiration time from a JWT token.

        Args:
            token (str): The JWT token.

        Returns:
            datetime | None: The expiration datetime in UTC, or None if not found.

        Raises:
            JWTDecodeError: If the token is invalid.
            JWTExpiredError: If the token is expired.
        """
        try:
            decoded_token = jwt.decode(
                token,
                JWTHandler.secret_key,
                algorithms=[JWTHandler.algorithm],
                options={"verify_exp": True},
            )
            exp = decoded_token.get("exp")
            if exp:
                return datetime.fromtimestamp(exp).replace(tzinfo=timezone.utc)
            return None
        except jwt.exceptions.DecodeError as exception:
            raise JWTDecodeError() from exception
        except jwt.exceptions.ExpiredSignatureError as exception:
            raise JWTExpiredError() from exception
