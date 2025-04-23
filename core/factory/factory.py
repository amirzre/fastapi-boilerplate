from functools import partial

from fastapi import Depends

from app.controllers import AuthController, PostController, UserController
from app.models import Post, User
from app.repositories import PostRepository, UserRepository
from core.db import get_session


class Factory:
    """
    A factory class for creating and providing instances of various controllers
    and repositories, which are used throughout the application.

    This class is responsible for instantiating controllers and repositories and
    ensuring the correct dependencies are injected, such as database sessions.
    """

    user_repository = partial(UserRepository, User)
    post_repository = partial(PostRepository, Post)

    def get_user_controller(self, db_session=Depends(get_session)):
        """
        Instantiates and returns a UserController with the required dependencies.

        Args:
            db_session (AsyncSession, optional): The database session to be used for repository operations.
                Defaults to the result of Depends(get_session), which provides the session dependency.

        Returns:
            UserController: An instance of the UserController.
        """
        return UserController(user_repository=self.user_repository(db_session=db_session))

    def get_auth_controller(self, db_session=Depends(get_session)):
        """
        Instantiates and returns an AuthController with the required dependencies.

        Args:
            db_session (AsyncSession, optional): The database session to be used for repository operations.
                Defaults to the result of Depends(get_session), which provides the session dependency.

        Returns:
            AuthController: An instance of the AuthController.
        """
        return AuthController(user_repository=self.user_repository(db_session=db_session))

    def get_post_controller(self, db_session=Depends(get_session)):
        """
        Instantiates and returns a PostController with the required dependencies.

        Args:
            db_session (AsyncSession, optional): The database session to be used for repository operations.
                Defaults to the result of Depends(get_session), which provides the session dependency.

        Returns:
            PostController: An instance of the PostController.
        """
        return PostController(
            post_repository=self.post_repository(db_session=db_session),
            user_repository=self.user_repository(db_session=db_session),
        )
