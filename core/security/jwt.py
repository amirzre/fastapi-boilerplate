from datetime import datetime, timedelta, timezone

import jwt
from fastapi import status

from core.config import config
from core.exceptions import CustomException
from core.i18n import translate as _


class JWTDecodeError(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = _("Invalid token.")


class JWTExpiredError(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = _("Token expired.")


class JWTHandler:
    secret_key = config.SECRET_KEY
    algorithm = config.JWT_ALGORITHM
    access_token_expire = config.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire = config.REFRESH_TOKEN_EXPIRE_MINUTES

    @staticmethod
    def encode(payload: dict) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTHandler.access_token_expire)
        payload.update({"exp": expire})
        return jwt.encode(
            payload=payload,
            key=JWTHandler.secret_key,
            algorithm=JWTHandler.algorithm,
        )

    @staticmethod
    def encode_refresh_token(payload: dict) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTHandler.refresh_token_expire)
        payload.update({"exp": expire})
        return jwt.encode(
            payload=payload,
            key=JWTHandler.secret_key,
            algorithm=JWTHandler.algorithm,
        )

    @staticmethod
    def decode(token: str) -> dict:
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
