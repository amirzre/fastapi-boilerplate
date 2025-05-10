from secrets import token_hex

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from core.config import config


class SessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures each request has a unique session ID stored in cookies.
    If a session ID does not exist, it generates and sets a new one.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        session_id = request.cookies.get("Session-Id")
        if not session_id:
            session_id = token_hex(16)

        response = await call_next(request)
        response.set_cookie(
            key="Session-Id", value=session_id, httponly=True, samesite="strict", max_age=config.SESSION_EXPIRE_MINUTES
        )
        return response
