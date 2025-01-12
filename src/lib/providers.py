from collections.abc import AsyncGenerator
from typing import AsyncIterator

from aiogram import Bot
from aiogram.types import TelegramObject
from dishka import Provider, from_context, Scope, provide
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.database import Database
from src.settings.config import PostgresConfig, BotSettings


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


class AiogramProvider(Provider):
    """Провайдер для Aiogramm"""
    event = from_context(TelegramObject, scope=Scope.REQUEST)


class PostgresProvider(Provider):
    """Провайдер для Postgres."""

    postgres_config = from_context(provides=PostgresConfig, scope=Scope.APP)
    database = provide(Database, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def session(self, database: Database) -> AsyncIterator[AsyncSession]:
        """Получение сессии."""
        async with database.get_db_session() as session:
            yield session
            await session.close()



class BotProvider(Provider):
    """Провайдер для бота."""

    bot_settings = from_context(provides=BotSettings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def bot(self, bot_settings: BotSettings) -> Bot:
        """Получение объекта текущего бота."""
        return Bot(bot_settings.token.get_secret_value())

