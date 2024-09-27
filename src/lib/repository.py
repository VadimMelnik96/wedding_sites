from abc import ABC, abstractmethod
from typing import Type, Any, Iterable

from pydantic import BaseModel
from sqlalchemy import (
    insert,
    select,
    update,
    delete,
    ScalarResult,
    Select,
    Result,
    ValuesBase,
    Delete,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.spi.persistent.models.base import Base
from src.lib.exceptions import NotFoundError


class Repository(ABC):
    """Абстрактный CRUD - репозиторий"""

    @abstractmethod
    async def create(self, create_dto):
        pass

    @abstractmethod
    async def get_list(self, filters):
        pass

    @abstractmethod
    async def get_one(self, filters):
        pass

    @abstractmethod
    async def update(self, update_dto, filters):
        pass

    @abstractmethod
    async def delete(self):
        pass

    @abstractmethod
    async def bulk_create(self, data: list):
        pass


class SQLAlchemyRepository(Repository):
    """
    CRUD - репозиторий для SQLAlchemy
    При инициализации наследников определяется модель и стандартное dto ответа
    """

    model: Type[Base] = None
    response_dto: BaseModel = None

    def __init__(
        self, session: AsyncSession,
    ):
        self.session = session
        self.auto_commit = None
        self.auto_refresh = None

    async def create(
            self,
            create_dto: BaseModel,
            response_dto: Base | None = None,
            auto_commit: bool = True,
    ) -> BaseModel:
        stmt = (
            insert(self.model).values(**create_dto.model_dump()).returning(self.model)
        )
        res = await self._execute(stmt)
        await self._flush_or_commit(auto_commit)
        return self.to_dto(res.scalar_one(), response_dto)

    async def bulk_create(
            self,
            bulk_create_dto: list[BaseModel],
            response_dto: BaseModel | None = None,
            auto_commit: bool = True,
    ) -> BaseModel:
        stmt = (
            insert(self.model).values([entity.model_dump() for entity in bulk_create_dto]).returning(self.model)
        )
        res = await self._execute(stmt)
        await self._flush_or_commit(auto_commit)
        return self.to_dto(res.scalar_one(), response_dto)

    async def get_one(self, filters: BaseModel, response_dto: BaseModel | None = None) -> BaseModel:
        stmt = select(self.model).filter_by(**filters.model_dump(exclude_none=True))
        result = await self._execute(stmt)
        instance = result.scalar_one_or_none()
        self.check_not_found(instance)
        return self.to_dto(instance, response_dto)

    async def get_list(
        self,
        response_dto: Base | None = None,
        filters: BaseModel = None,
    ) -> list[BaseModel]:
        stmt = select(self.model).filter_by(**filters.model_dump())
        res = await self._execute(stmt)
        return self.to_dto(res.scalars())

    async def update(
        self,
        update_dto: BaseModel,
        filters: BaseModel,
        response_dto: BaseModel | None = None,
        auto_commit: bool = True,
    ) -> BaseModel:
        stmt = (
            update(self.model)
            .values(**update_dto.model_dump(exclude_unset=True))
            .filter_by(**filters.model_dump(exclude_unset=True))
            .returning(self.model)
        )
        res = (await self._execute(stmt)).scalar_one_or_none()
        self.check_not_found(res)
        await self._flush_or_commit(auto_commit)
        return self.to_dto(res, response_dto)

    async def delete(self, auto_commit: bool = True, **filters) -> None:
        stmt = delete(self.model).filter_by(**filters)
        result = await self._execute(stmt)
        if result.rowcount == 0:
            raise NotFoundError(
                f"По данным запроса в таблице {self.model.__tablename__} записей не найдено"
            )
        await self._flush_or_commit(auto_commit)

    def to_dto(
        self, instance: Base | ScalarResult, dto: BaseModel = None
    ) -> BaseModel | list[BaseModel]:
        """
        Метод, преобразующий модели SQLAlchemy к dto.
        """
        if dto is None:
            dto = self.response_dto
        if not isinstance(instance, ScalarResult | list):
            return dto.model_validate(instance, from_attributes=True)
        return [dto.model_validate(row, from_attributes=True) for row in instance]

    async def _flush_or_commit(self, auto_commit: bool | None) -> None:
        if auto_commit is None:
            auto_commit = self.auto_commit
        return (
            await self.session.commit() if auto_commit else await self.session.flush()
        )

    async def _refresh(
        self,
        instance: Base,
        auto_refresh: bool | None,
        attribute_names: Iterable[str] | None = None,
        with_for_update: bool | None = None,
    ) -> None:
        if auto_refresh is None:
            auto_refresh = self.auto_refresh

        return (
            await self.session.refresh(
                instance,
                attribute_names=attribute_names,
                with_for_update=with_for_update,
            )
            if auto_refresh
            else None
        )

    @staticmethod
    def check_not_found(item_or_none: Base | None) -> Base:
        if item_or_none is None:
            msg = "No item found when one was expected"
            raise NotFoundError(msg)
        return item_or_none

    async def _execute(
        self, statement: ValuesBase | Select[Any] | Delete
    ) -> Result[Any]:
        return await self.session.execute(statement)
