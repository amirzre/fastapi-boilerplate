from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post, PostStatus, User
from app.repositories.post import PostRepository
from app.schemas.request import PostFilterParams
from core.repository import BaseRepository

fake = Faker()


@pytest.mark.asyncio
class TestPostRepository:
    """Test suite for verifying PostRepository functionality including filtering, sorting and pagination."""

    @pytest_asyncio.fixture
    async def user(self, db_session: AsyncSession) -> User:
        """Fixture creating and returning a test user with activated account."""
        user_repo = BaseRepository(User, db_session)
        data = {
            "email": fake.email(),
            "uuid": fake.uuid4(),
            "password": fake.password(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "activated": True,
            "role": "USER",
        }
        user = await user_repo.create(data)
        return user

    @pytest_asyncio.fixture
    def post_repo(self, db_session: AsyncSession) -> PostRepository:
        """Fixture providing initialized PostRepository instance."""
        return PostRepository(model=Post, db_session=db_session)

    @pytest_asyncio.fixture
    async def posts(self, user: User, post_repo: PostRepository) -> list[Post]:
        """Fixture creating test posts with different statuses and timestamps."""
        now = datetime.now(timezone.utc)
        posts = []
        posts.append(
            await post_repo.create(
                {
                    "title": "Draft Title",
                    "content": fake.text(),
                    "status": PostStatus.DRAFT,
                    "user_id": user.uuid,
                    "created": now - timedelta(days=2),
                    "updated": now - timedelta(days=2),
                }
            )
        )
        posts.append(
            await post_repo.create(
                {
                    "title": "Published Title",
                    "content": fake.text(),
                    "status": PostStatus.PUBLISHED,
                    "user_id": user.uuid,
                    "created": now - timedelta(days=1),
                    "updated": now - timedelta(days=1),
                }
            )
        )
        posts.append(
            await post_repo.create(
                {
                    "title": "Another Published",
                    "content": fake.text(),
                    "status": PostStatus.PUBLISHED,
                    "user_id": user.uuid,
                    "created": now,
                    "updated": now,
                }
            )
        )
        return posts

    async def test_get_by_uuid_found(self, posts, post_repo: PostRepository):
        """Verify retrieval of existing post by UUID returns correct post instance."""
        target = posts[1]
        result = await post_repo.get_by_uuid(target.uuid)

        assert result is not None
        assert result.uuid == target.uuid

    async def test_get_by_uuid_not_found(self, post_repo: PostRepository):
        """Verify attempt to retrieve non-existent post by UUID returns None."""
        result = await post_repo.get_by_uuid(uuid4())

        assert result is None

    async def test_get_posts_by_user_no_filters(self, user, posts, post_repo: PostRepository):
        """Test retrieving all user posts when no filters are applied."""
        params = PostFilterParams(
            title=None,
            status=None,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
            order_by="created",
            limit=10,
            offset=0,
        )
        items, total = await post_repo.get_posts_by_user(user.uuid, params)

        assert total == len(posts)
        assert set(p.uuid for p in items) == set(p.uuid for p in posts)

    async def test_title_filter(self, user, posts, post_repo: PostRepository):
        """Test filtering posts by title substring match."""
        params = PostFilterParams(
            title="Another",
            status=None,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
            order_by="created",
            limit=10,
            offset=0,
        )
        items, total = await post_repo.get_posts_by_user(user.uuid, params)

        assert total == 1
        assert items[0].title == "Another Published"

    async def test_status_filter(self, user, posts, post_repo: PostRepository):
        """Verify filtering posts by publication status returns correct subset."""
        params = PostFilterParams(
            title=None,
            status=PostStatus.PUBLISHED,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
            order_by="created",
            limit=10,
            offset=0,
        )
        items, total = await post_repo.get_posts_by_user(user.uuid, params)

        assert total == 2
        assert all(p.status == PostStatus.PUBLISHED for p in items)

    async def test_created_date_range(self, user, posts, post_repo: PostRepository):
        """Test filtering posts by creation date range (from date)."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        params = PostFilterParams(
            title=None,
            status=None,
            created_from=cutoff,
            created_to=None,
            updated_from=None,
            updated_to=None,
            order_by="created",
            limit=10,
            offset=0,
        )
        items, total = await post_repo.get_posts_by_user(user.uuid, params)

        assert total == 1
        assert all(p.created > cutoff for p in items)

    async def test_updated_date_range(self, user, posts, post_repo: PostRepository):
        """Test filtering posts by update date range (to date inclusive)."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        params = PostFilterParams(
            title=None,
            status=None,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=cutoff,
            order_by="updated",
            limit=10,
            offset=0,
        )
        items, total = await post_repo.get_posts_by_user(user.uuid, params)

        assert total == 2
        assert all(p.updated <= cutoff for p in items)

    async def test_order_by_updated(self, user, posts, post_repo: PostRepository):
        """Verify posts can be ordered by update timestamp in ascending order."""
        params = PostFilterParams(
            title=None,
            status=None,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
            order_by="updated",
            limit=10,
            offset=0,
        )
        items, _ = await post_repo.get_posts_by_user(user.uuid, params)
        updated_list = [p.updated for p in items]

        assert updated_list == sorted(updated_list)

    async def test_pagination(self, user, posts, post_repo: PostRepository):
        """Test pagination functionality with limit and offset parameters."""
        params = PostFilterParams(
            title=None,
            status=None,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
            order_by="created",
            limit=1,
            offset=1,
        )
        items, total = await post_repo.get_posts_by_user(user.uuid, params)

        assert total == len(posts)
        assert len(items) == 1
