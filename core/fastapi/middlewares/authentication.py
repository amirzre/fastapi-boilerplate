from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from core.exceptions import UnauthorizedException
from core.i18n import translate as _
from core.security import JWTHandler


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = request.cookies.get("Access-Token")
        if token:
            try:
                decoded_token = JWTHandler.decode(token=token)
                user_uuid = decoded_token.get("uuid")
                user_role = decoded_token.get("role")

                if user_uuid and user_role:
                    request.state.user = {"uuid": user_uuid, "role": user_role}
                else:
                    raise UnauthorizedException(message=_("Invalid token."))
            except Exception as e:
                raise UnauthorizedException(message=_(f"Authentication failed: {str(e)}"))
        else:
            request.state.user = None

        response = await call_next(request)
        return response
