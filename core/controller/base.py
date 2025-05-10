from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from core.db import Base, Transactional
from core.exceptions import NotFoundException
from core.repository import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class BaseController(Generic[ModelType]):
    """
    A base class for data controllers providing standard CRUD operations.

    This class provides methods for retrieving, creating, and deleting data from
    the repository. It supports operations based on `id` and `uuid` fields, along
    with pagination for fetching multiple records.
    """

    def __init__(self, model: Type[ModelType], repository: BaseRepository):
        """
        Initializes the controller with the model and repository.

        Args:
            model (Type[ModelType]): The model class the controller will handle.
            repository (BaseRepository): The repository instance to interact with the database.
        """
        self.model_class = model
        self.repository = repository

    async def get_by_id(self, id_: int) -> ModelType | Sequence[ModelType]:
        """
        Retrieves the model instance matching the provided ID.

        Args:
            id_ (int): The ID of the model to retrieve.

        Returns:
            ModelType | Sequence[ModelType]: A single model instance or a sequence
            of models matching the ID.

        Raises:
            NotFoundException: If no model instance is found with the given ID.
        """

        db_obj = await self.repository.get_by(field="id", value=id_, unique=True)
        if not db_obj:
            raise NotFoundException(f"{self.model_class.__tablename__.title()} with id: {id} does not exist")

        return db_obj

    async def get_by_uuid(self, uuid: UUID) -> ModelType | Sequence[ModelType]:
        """
        Retrieves the model instance matching the provided UUID.

        Args:
            uuid (UUID): The UUID of the model to retrieve.

        Returns:
            ModelType | Sequence[ModelType]: A single model instance or a sequence
            of models matching the UUID.

        Raises:
            NotFoundException: If no model instance is found with the given UUID.
        """

        db_obj = await self.repository.get_by(field="uuid", value=uuid, unique=True)
        if not db_obj:
            raise NotFoundException(f"{self.model_class.__tablename__.title()} with id: {uuid} does not exist")
        return db_obj

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Retrieves a list of model instances based on pagination parameters.

        Args:
            skip (int, optional): The number of records to skip (default is 0).
            limit (int, optional): The maximum number of records to return (default is 100).

        Returns:
            Sequence[ModelType]: A sequence (list or tuple) of model instances.

        Notes:
            Pagination is useful for querying large datasets efficiently.
        """

        response = await self.repository.get_all(skip, limit)
        return response

    @Transactional()
    async def create(self, attributes: dict[str, Any]) -> ModelType:
        """
        Creates a new model instance in the database with the provided attributes.

        Args:
            attributes (dict): A dictionary containing the attributes for the new model.

        Returns:
            ModelType: The newly created model instance.

        Raises:
            Any: Raises any exception raised by the repository during creation.
        """
        create = await self.repository.create(attributes)
        return create

    @Transactional()
    async def delete(self, model: ModelType) -> None:
        """
        Deletes the provided model instance from the database.

        Args:
            model (ModelType): The model instance to delete.

        Returns:
            None

        Raises:
            Any: Raises any exception raised by the repository during deletion.
        """
        return await self.repository.delete(model)
