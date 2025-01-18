from functools import partial

from fastapi import Depends

from app.controllers import AuthController, PostController, UserController
from app.models import Post, User
from app.repositories import PostRepository, UserRepository
from core.db import get_session


class Factory:
    """
    This is the factory container that will instantiate all the controllers and
    repositories which can be accessed by the rest of the application.
    """

    user_repository = partial(UserRepository, User)
    post_repository = partial(PostRepository, Post)

    def get_user_controller(self, db_session=Depends(get_session)):
        return UserController(user_repository=self.user_repository(db_session=db_session))

    def get_auth_controller(self, db_session=Depends(get_session)):
        return AuthController(user_repository=self.user_repository(db_session=db_session))

    def get_post_controller(self, db_session=Depends(get_session)):
        return PostController(post_repository=self.post_repository(db_session=db_session))
