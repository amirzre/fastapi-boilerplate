from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api import router
from core.cache import Cache, CustomKeyMaker, RedisBackend
from core.config import config
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthenticationMiddleware,
    ResponseLoggerMiddleware,
    SessionMiddleware,
    SQLAlchemyMiddleware,
)
from core.responses import ResponseStatus


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = status.HTTP_401_UNAUTHORIZED, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return ORJSONResponse(
        status_code=status_code,
        content={
            "header": {"status": ResponseStatus.FAILURE, "message": message, "code": error_code},
            "content": None,
        },
    )


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return ORJSONResponse(
            status_code=exc.code,
            content={
                "header": {"status": ResponseStatus.FAILURE, "message": exc.message, "code": exc.error_code},
                "content": None,
            },
        )


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[str(url) for url in config.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(SessionMiddleware),
        Middleware(AuthenticationMiddleware),
        Middleware(SQLAlchemyMiddleware),
        Middleware(ResponseLoggerMiddleware),
    ]
    return middleware


def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def create_app() -> FastAPI:
    app_ = FastAPI(
        title=config.APP_TITLE,
        description="FastAPI Boilerplate",
        version=config.RELEASE_VERSION,
        docs_url=None if config.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if config.ENVIRONMENT == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    return app_


app = create_app()
