from datetime import datetime, timezone
from typing import Any, Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import ScalarResult, Select, Subquery, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from core.db import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic base class for asynchronous database repositories using SQLAlchemy.

    Provides common CRUD operations and utilities for handling model instances.
    """

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        """
        Initialize the repository.

        Args:
            model: The SQLAlchemy model class.
            db_session: The asynchronous database session.
        """
        self.session = db_session
        self.model_class: Type[ModelType] = model

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Retrieve all model instances with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            A list of model instances.
        """
        query = self._query()
        query = query.offset(skip).limit(limit)

        return await self._all(query)

    async def get_by(
        self,
        field: str,
        value: Any,
        unique: bool = False,
    ) -> ModelType | Sequence[ModelType]:
        """
        Retrieve model instances matching a field and value.

        Args:
            field: Field name to filter by.
            value: Value to match against the field.
            unique: If True, return a single instance; otherwise, return all matching instances.

        Returns:
            A single model instance or a list of model instances.
        """
        query = self._query()
        query = await self._get_by(query, field, value)

        if unique:
            return await self._one(query)

        return await self._all(query)

    async def create(self, attributes: dict[str, Any] | BaseModel) -> ModelType:
        """
        Create a new model instance.

        Args:
            attributes: Dictionary or Pydantic model containing the attributes.

        Returns:
            The created model instance.
        """
        data = attributes.model_dump(exclude_unset=True) if isinstance(attributes, BaseModel) else attributes

        for key, value in data.items():
            if isinstance(value, datetime) and value.tzinfo is not None:
                data[key] = value.replace(tzinfo=None)

        model = self.model_class(**data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def update(self, model: ModelType, attributes: dict[str, Any] | BaseModel) -> ModelType:
        """
        Update an existing model instance.

        Args:
            model: The model instance to update.
            attributes: Dictionary or Pydantic model containing updated fields.

        Returns:
            The updated model instance.
        """
        if attributes:
            data = attributes.model_dump(exclude_unset=True) if isinstance(attributes, BaseModel) else attributes

            for key, value in data.items():
                if isinstance(value, datetime):
                    if value.tzinfo is not None:
                        value = value.replace(tzinfo=None)
                    data[key] = value
                setattr(model, key, value)

        if hasattr(model, "updated"):
            setattr(model, "updated", datetime.now())

        await self.session.commit()
        return model

    async def delete(self, model: ModelType) -> ModelType:
        """
        Soft delete a model instance by setting the `deleted` timestamp.

        Args:
            model: The model instance to soft delete.

        Returns:
            The soft-deleted model instance.
        """
        if hasattr(model, "deleted"):
            setattr(model, "deleted", datetime.now(timezone.utc))
            await self.session.commit()

        return model

    async def remove(self, model: ModelType) -> None:
        """
        Permanently delete a model instance.

        Args:
            model: The model instance to delete.
        """
        await self.session.delete(model)
        await self.session.commit()

    def _query(
        self,
        order_: dict | None = None,
    ) -> Select:
        """
        Construct a base SELECT query for the model.

        Args:
            order_: Optional dictionary specifying order clauses.

        Returns:
            A SQLAlchemy Select object.
        """
        query = select(self.model_class)
        if hasattr(self.model_class, "deleted"):
            query = query.where(getattr(self.model_class, "deleted").is_(None))
        query = self._maybe_ordered(query, order_)
        return query

    async def _all(self, query: Select) -> Sequence[ModelType]:
        """
        Execute a query and return all results.

        Args:
            query: The SELECT query to execute.

        Returns:
            A list of model instances.
        """
        result: ScalarResult[ModelType] = await self.session.scalars(query)
        return result.all()

    async def _all_unique(self, query: Select) -> Sequence[ModelType]:
        """
        Execute a query and return all unique results.

        Args:
            query: The SELECT query to execute.

        Returns:
            A list of unique model instances.
        """
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def _first(self, query: Select) -> ModelType | None:
        """
        Execute a query and return the first result.

        Args:
            query: The SELECT query to execute.

        Returns:
            The first model instance or None.
        """
        result: ScalarResult[ModelType] = await self.session.scalars(query)
        return result.first()

    async def _one_or_none(self, query: Select) -> ModelType | None:
        """
        Execute a query and return exactly one or no result.

        Args:
            query: The SELECT query to execute.

        Returns:
            The matched model instance or None.
        """
        result: ScalarResult[ModelType] = await self.session.scalars(query)
        return result.one_or_none()

    async def _one(self, query: Select) -> ModelType:
        """
        Execute a query and return exactly one result.

        Raises:
            NoResultFound: If no matching result is found.

        Args:
            query: The SELECT query to execute.

        Returns:
            The matched model instance.
        """
        result: ScalarResult[ModelType] = await self.session.scalars(query)
        return result.one()

    async def _count(self, query: Select) -> int:
        """
        Count the number of results returned by a query.

        Args:
            query: The SELECT query to execute.

        Returns:
            The count of matching records.
        """
        subquery: Subquery = query.subquery()
        count_query = select(func.count()).select_from(subquery)
        result: ScalarResult[int] = await self.session.scalars(count_query)
        return result.one()

    async def _sort_by(
        self,
        query: Select,
        sort_by: str,
        order: str | None = "asc",
        model: Type[ModelType] | None = None,
        case_insensitive: bool = False,
    ) -> Select:
        """
        Sort a query by the specified column.

        Args:
            query: The SELECT query to sort.
            sort_by: The column name to sort by.
            order: 'asc' or 'desc'.
            model: Optional model to use for attribute lookup.
            case_insensitive: If True, apply case-insensitive sorting.

        Returns:
            The sorted query.
        """
        model = model or self.model_class

        order_column = None

        if case_insensitive:
            order_column = func.lower(getattr(model, sort_by))
        else:
            order_column = getattr(model, sort_by)

        if order == "desc":
            return query.order_by(order_column.desc())

        return query.order_by(order_column.asc())

    async def _get_by(self, query: Select, field: str, value: Any) -> Select:
        """
        Filter a query by a field and value.

        Args:
            query: The SELECT query to filter.
            field: Field name to filter by.
            value: Value to match.

        Returns:
            The filtered query.
        """
        return query.where(getattr(self.model_class, field) == value)

    def _maybe_ordered(self, query: Select, order_: dict | None = None) -> Select:
        """
        Apply ordering to a query if order parameters are provided.

        Args:
            query: The SELECT query to order.
            order_: Dictionary with 'asc' and/or 'desc' order keys.

        Returns:
            The ordered query.
        """
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    query = query.order_by(getattr(self.model_class, order).asc())
            else:
                for order in order_["desc"]:
                    query = query.order_by(getattr(self.model_class, order).desc())

        return query
