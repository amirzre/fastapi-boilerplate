from contextvars import ContextVar, Token
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql.expression import Delete, Insert, Update

from core.config import config

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    """
    Retrieves the current session context.

    This function is used to get the session ID set within the current context.

    Returns:
        str: The current session ID.
    """
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    """
    Sets the session context with the given session ID.

    Args:
        session_id (str): The session ID to be set in the context.

    Returns:
        Token: A token that can be used to reset the session context.
    """
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    """
    Resets the session context to the state prior to setting it.

    Args:
        context (Token): The token to reset the context to.
    """
    session_context.reset(context)


engines = {
    "writer": create_async_engine(
        config.POSTGRES_URL,
        pool_recycle=config.SQLALCHEMY_POOL_RECYCLE,
        max_overflow=config.SQLALCHEMY_MAX_OVERFLOW,
        pool_size=config.SQLALCHEMY_POOL_SIZE,
        pool_timeout=config.SQLALCHEMY_POOL_TIMEOUT,
    ),
    "reader": create_async_engine(
        config.POSTGRES_URL,
        pool_recycle=config.SQLALCHEMY_POOL_RECYCLE,
        max_overflow=config.SQLALCHEMY_MAX_OVERFLOW,
        pool_size=config.SQLALCHEMY_POOL_SIZE,
        pool_timeout=config.SQLALCHEMY_POOL_TIMEOUT,
    ),
}


class RoutingSession(Session):
    """
    Custom SQLAlchemy session that routes queries to the appropriate database engine.

    Queries involving modifications (INSERT, UPDATE, DELETE) are routed to the writer engine,
    while other queries (SELECT) are routed to the reader engine.
    """

    def get_bind(self, mapper=None, clause=None, **kwargs):
        """
        Determines the appropriate database engine based on the operation.

        Args:
            mapper: Optional mapper for the query.
            clause: The SQL expression for the query.

        Returns:
            sync_engine: The corresponding database engine (writer or reader).
        """
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines["writer"].sync_engine
        return engines["reader"].sync_engine


async_session_factory = async_sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
)

session: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)


async def get_session():
    """
    Provides an asynchronous database session for dependency injection.

    This method yields a session that can be used within a context for interacting
    with the database. The session is automatically closed after use.

    Yields:
        AsyncSession: The database session to be used within the context.
    """
    try:
        yield session
    finally:
        await session.close()


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    This class serves as the foundation for defining database models using SQLAlchemy's
    declarative system. All database models should inherit from this base class.
    """
