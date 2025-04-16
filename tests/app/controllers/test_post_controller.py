from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest
from pydantic import UUID4

from app.controllers import PostController
from app.models import Post, PostStatus
from app.repositories import PostRepository, UserRepository
from app.schemas.request import CreatePostRequest, PostFilterParams, UpdatePostRequest
from app.schemas.response import PostResponse
from core.exceptions import NotFoundException


@pytest.mark.asyncio
class TestPostController:
    """
    Test suite for PostController class.

    This class contains test cases for all the methods in the PostController,
    including successful operations and error cases.
    """

    @pytest.fixture
    def user_repository(self) -> AsyncMock:
        """
        Fixture that provides a mock user repository.

        Returns:
            AsyncMock: A mock instance of UserRepository.
        """
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def post_repository(self) -> AsyncMock:
        """
        Fixture that provides a mock post repository.

        Returns:
            AsyncMock: A mock instance of PostRepository.
        """
        return AsyncMock(spec=PostRepository)

    @pytest.fixture
    def post_controller(self, post_repository: AsyncMock, user_repository: AsyncMock) -> PostController:
        """
        Fixture that provides an instance of PostController with mock repositories.

        Args:
            post_repository: Mock post repository
            user_repository: Mock user repository

        Returns:
            PostController: An instance of PostController for testing.
        """
        return PostController(post_repository=post_repository, user_repository=user_repository)

    @pytest.fixture
    def mock_uuid(self) -> UUID4:
        """
        Fixture that provides a mock UUID.

        Returns:
            UUID4: A mock UUID for testing.
        """
        return UUID("a3b8f042-1e16-4f0a-a8f0-421e16df0a5f")

    @pytest.fixture
    def mock_post(self) -> Mock:
        """
        Fixture that provides a mock Post instance.

        Returns:
            Mock: A mock Post instance with predefined attributes.
        """
        post = Mock(spec=Post)
        post.uuid = UUID("a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")
        post.title = "Test Post"
        post.status = PostStatus.DRAFT
        post.user_id = UUID("a4b8f042-1e16-4f0a-a8f0-421e16df0a2f")
        post.__acl__ = Mock(return_value=[])
        return post

    async def test_get_user_posts_success(
        self,
        post_controller: PostController,
        user_repository: AsyncMock,
        post_repository: AsyncMock,
        mock_uuid: UUID4,
        mock_post: Mock,
    ) -> None:
        """Test successful retrieval of user posts."""
        filter_params = PostFilterParams(
            limit=10,
            offset=0,
            title=None,
            status=None,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
        )
        user_repository.get_by_uuid.return_value = Mock(uuid=mock_uuid)
        post_repository.get_posts_by_user.return_value = ([mock_post], 1)

        result = await post_controller.get_user_posts(user_id=mock_uuid, filter_params=filter_params)

        assert result.total == 1
        assert result.limit == filter_params.limit
        assert result.offset == filter_params.offset
        assert len(result.items) == 1
        user_repository.get_by_uuid.assert_called_once_with(uuid=mock_uuid)

    async def test_get_user_posts_user_not_found(
        self, post_controller: PostController, user_repository: AsyncMock, mock_uuid: UUID4
    ) -> None:
        """Test get_user_posts when user doesn't exist."""
        filter_params = PostFilterParams(
            limit=10,
            offset=0,
            title=None,
            status=None,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
        )
        user_repository.get_by_uuid.return_value = None

        with pytest.raises(NotFoundException):
            await post_controller.get_user_posts(user_id=mock_uuid, filter_params=filter_params)

    async def test_get_post_success(
        self, post_controller: PostController, post_repository: AsyncMock, mock_uuid: UUID4, mock_post: Mock
    ) -> None:
        """Test successful retrieval of a single post."""
        post_repository.get_by_uuid.return_value = mock_post

        result = await post_controller.get_post(post_uuid=mock_uuid)

        assert isinstance(result, PostResponse)
        assert result.uuid == mock_post.uuid
        assert result.title == mock_post.title
        assert result.status == mock_post.status
        assert result.user_id == mock_post.user_id

    async def test_get_post_not_found(
        self, post_controller: PostController, post_repository: AsyncMock, mock_uuid: UUID4
    ) -> None:
        """Test get_post when post doesn't exist."""
        post_repository.get_by_uuid.return_value = None

        with pytest.raises(NotFoundException):
            await post_controller.get_post(post_uuid=mock_uuid)

    async def test_create_post_success(
        self, post_controller: PostController, user_repository: AsyncMock, post_repository: AsyncMock, mock_post: Mock
    ) -> None:
        """Test successful post creation."""
        create_request = CreatePostRequest(
            title="Test Post", content="Test content", status=PostStatus.DRAFT, user_id=mock_post.user_id
        )
        user_repository.get_by_uuid.return_value = Mock(uuid=mock_post.user_id)
        post_repository.create.return_value = mock_post

        with patch("core.db.session.session_context", new_callable=AsyncMock):
            result = await post_controller.create_post(create_post_request=create_request)

        assert isinstance(result, PostResponse)
        assert result.uuid == mock_post.uuid
        assert result.title == mock_post.title
        post_repository.create.assert_called_once_with(attributes=create_request)

    async def test_update_post_success(
        self, post_controller: PostController, post_repository: AsyncMock, mock_uuid: UUID4, mock_post: Mock
    ) -> None:
        """Test successful post update."""
        update_request = UpdatePostRequest(
            title="Updated Title",
            status=PostStatus.PUBLISHED,
            content="Updated content",
        )
        post_repository.get_by_uuid.return_value = mock_post
        post_repository.update.return_value = mock_post

        with patch("core.db.session.session_context", new_callable=AsyncMock):
            result = await post_controller.update_post(post_uuid=mock_uuid, update_post_request=update_request)

        assert isinstance(result, PostResponse)
        assert result.uuid == mock_post.uuid
        post_repository.update.assert_called_once_with(model=mock_post, attributes=update_request)

    async def test_delete_post_success(
        self, post_controller: PostController, post_repository: AsyncMock, mock_uuid: UUID4, mock_post: Mock
    ) -> None:
        """Test successful post deletion."""
        post_repository.get_by_uuid.return_value = mock_post

        with patch("core.db.session.session_context", new_callable=AsyncMock):
            await post_controller.delete_post(post_uuid=mock_uuid)

        post_repository.delete.assert_called_once_with(model=mock_post)
