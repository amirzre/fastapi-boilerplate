import pytest
import pytest_asyncio
from faker import Faker

from app.models import User
from core.repository import BaseRepository

fake = Faker()


@pytest.mark.asyncio
class TestBaseRepository:
    def _user_data_generator(self):
        return {
            "email": fake.email(),
            "uuid": fake.uuid4(),
            "password": fake.password(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "activated": fake.boolean(),
            "role": "USER",
        }

    @pytest_asyncio.fixture
    async def repository(self, db_session):
        return BaseRepository(model=User, db_session=db_session)

    @pytest_asyncio.fixture
    async def user_instance(self, repository: BaseRepository[User]):
        user = await repository.create(self._user_data_generator())
        await repository.session.commit()
        return user

    async def test_create(self, repository):
        user = await repository.create(self._user_data_generator())
        await repository.session.commit()
        assert user.id is not None

    async def test_get_all(self, repository, user_instance):
        users = await repository.get_all()
        assert len(users) >= 1
        assert user_instance in users

    async def test_get_all_with_limit_and_skip(self, repository):
        await repository.create(self._user_data_generator())
        await repository.create(self._user_data_generator())
        await repository.session.commit()

        users = await repository.get_all(skip=1, limit=1)
        assert len(users) == 1

    async def test_get_by_existing_field(self, repository, user_instance):
        users = await repository.get_by(field="email", value=user_instance.email)
        for user in users:
            assert user.email == user_instance.email

    async def test_update(self, repository, user_instance):
        new_email = fake.email()
        updated_user = await repository.update(user_instance, {"email": new_email})
        await repository.session.commit()
        assert updated_user.email == new_email

    async def test_delete(self, repository, user_instance):
        await repository.delete(user_instance)
        await repository.session.commit()
        deleted_user = await repository.get_by(field="email", value=user_instance.email)
        assert len(deleted_user) == 0

    async def test_sorting(self, repository):
        await repository.create(self._user_data_generator())
        await repository.create(self._user_data_generator())
        await repository.session.commit()

        users = await repository.get_all()
        sorted_users_asc = await repository._sort_by(query=repository._query(), sort_by="email", order="asc")
        sorted_users_desc = await repository._sort_by(query=repository._query(), sort_by="email", order="desc")

        sorted_users_asc = await repository._all(sorted_users_asc)
        sorted_users_desc = await repository._all(sorted_users_desc)

        assert sorted_users_asc == sorted(users, key=lambda x: x.email)
        assert sorted_users_desc == sorted(users, key=lambda x: x.email, reverse=True)

    async def test_count(self, repository):
        await repository.create(self._user_data_generator())
        await repository.create(self._user_data_generator())
        await repository.session.commit()

        count = await repository._count(repository._query())
        assert count == 2

    async def test_first(self, repository):
        await repository.create(self._user_data_generator())
        await repository.create(self._user_data_generator())
        await repository.session.commit()

        user = await repository._first(repository._query())
        assert user is not None

    async def test_one_or_none(self, repository):
        user = await repository.create(self._user_data_generator())
        await repository.session.commit()

        result = await repository._one_or_none(repository._query().where(User.email == user.email))
        assert result.email == user.email

        result = await repository._one_or_none(repository._query().where(User.email == "nonexistent@example.com"))
        assert result is None
