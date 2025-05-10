from functools import wraps

from core.db import session


class Transactional:
    """
    A decorator class that wraps methods in a transaction.

    This class ensures that the function is executed within a database transaction.
    If an exception occurs, the transaction will be rolled back. Otherwise,
    the transaction is committed after the function executes successfully.
    """

    def __call__(self, func):
        @wraps(func)
        async def _transactional(*args, **kwargs):
            """
            Executes the function within a transaction, committing on success
            or rolling back on failure.

            Args:
                *args: Positional arguments passed to the decorated function.
                **kwargs: Keyword arguments passed to the decorated function.

            Returns:
                The result of the function if successful.

            Raises:
                Any exception raised by the decorated function will cause a rollback.
            """
            try:
                result = await func(*args, **kwargs)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

            return result

        return _transactional
