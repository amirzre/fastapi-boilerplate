import json
from enum import auto
from secrets import token_urlsafe

from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, TypeAdapter
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.enum import StrEnum


class EnvironmentType(StrEnum):
    DEVELOPMENT = auto()
    PRODUCTION = auto()
    TEST = auto()


class BaseConfig(BaseSettings):
    CORS_ORIGINS: list[AnyHttpUrl] = []

    @classmethod
    def cros_origins(cls, values):
        """Parse CORS ORIGINS as a JSON list from the env variable."""
        if isinstance(values.get("CORS_ORIGINS"), str):
            cors_origins = values["CORS_ORIGINS"]
            values["CORS_ORIGINS"] = TypeAdapter(list[AnyHttpUrl]).validate_python(json.loads(cors_origins))
        return values

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", env_nested_delimiter="__", case_sensitive=True)


class Config(BaseConfig):
    APP_TITLE: str = "FastAPI Application"
    DEBUG: bool = False
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    WORKERS: int = 1

    POSTGRES_URL: PostgresDsn = "postgresql+asyncpg://postgres:postgresql@127.0.0.1:5432/boilerplate"
    POSTGRES_TEST_URL: PostgresDsn = "postgresql+asyncpg://postgres:postgresql@127.0.0.1:5432/boilerplate-test"
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    SECRET_KEY: str = token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    SESSION_EXPIRE_MINUTES: int = 60 * 24

    SQLALCHEMY_POOL_SIZE: int = 15
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    SQLALCHEMY_MAX_OVERFLOW: int = 5

    RELEASE_VERSION: str = "1.0"


config: Config = Config()
