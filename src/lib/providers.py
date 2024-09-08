from collections.abc import AsyncGenerator

from dishka import Provider
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.database import Database


async def get_session(_: Provider, database: Database) -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии."""
    async with database.get_db_session() as session:
        try:
            yield session
        except exc.SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()
