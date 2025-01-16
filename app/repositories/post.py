from app.models import Post
from core.repository import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Post repository provides all the database operations for the Post model."""

    ...
