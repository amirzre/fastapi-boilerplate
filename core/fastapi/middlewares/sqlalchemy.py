from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

from core.db.session import reset_session_context, session, set_session_context


class SQLAlchemyMiddleware:
    """
    Middleware to manage SQLAlchemy session context per request.
    Generates a unique session ID and resets the session context after the request completes.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)

        try:
            await self.app(scope, receive, send)
        except Exception as exception:
            raise exception
        finally:
            await session.close()
            reset_session_context(context=context)
