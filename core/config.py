import json
from enum import StrEnum, auto
from pathlib import Path
from secrets import token_urlsafe

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(StrEnum):
    """
    Enumeration representing different types of environments for the application.

    Attributes:
        DEVELOPMENT (str): Represents the development environment.
        PRODUCTION (str): Represents the production environment.
        TEST (str): Represents the testing environment.
    """

    DEVELOPMENT = auto()
    PRODUCTION = auto()
    TEST = auto()


class BaseConfig(BaseSettings):
    """
    Base configuration settings for the FastAPI application.

    This class provides configuration values that are used throughout the application.
    It includes settings such as base directory, CORS origins, and other environment-based values.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CORS_ORIGINS: list[AnyHttpUrl] = []

    @classmethod
    def cros_origins(cls, values) -> dict:
        """
        Parse CORS_ORIGINS as a JSON list from the environment variable.

        This method attempts to convert the `CORS_ORIGINS` environment variable, which
        may be a JSON string, into a list of valid HTTP URLs. If the environment variable
        is not a valid JSON string, it will not be changed.

        Args:
            values (dict): The current configuration values.

        Returns:
            dict: The updated configuration values with `CORS_ORIGINS` as a list of `AnyHttpUrl`.
        """
        """Parse CORS ORIGINS as a JSON list from the env variable."""
        cors_origins = values.get("CORS_ORIGINS", "")
        if isinstance(cors_origins, str) and cors_origins:
            values["CORS_ORIGINS"] = json.loads(cors_origins)
        return values

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", env_nested_delimiter="__", case_sensitive=True)


class Config(BaseConfig):
    """
    Main configuration settings for the FastAPI application.

    This class extends the `BaseConfig` and provides specific configuration values
    for the application, including database URLs, Redis connection, security settings,
    and other operational parameters.
    """

    APP_TITLE: str = "FastAPI Application"
    DEBUG: bool = False
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    WORKERS: int = 1

    POSTGRES_URL: str = "postgresql+asyncpg://postgres:postgresql@127.0.0.1:5432/boilerplate"
    POSTGRES_TEST_URL: str = "postgresql+asyncpg://postgres:postgresql@127.0.0.1:5432/boilerplate-test"
    REDIS_URL: str = "redis://localhost:6379/0"

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
