from typing import AsyncIterator

from dishka import Provider, from_context, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from settings.config import PostgresConfig, BotSettings
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo
from src.adapters.spi.persistent.repositories.sites_repo import SitesRepo
from src.lib.database import Database
from src.services.ports.sites import ISitesService
from src.services.sites import SitesService


class ApplicationProvider(Provider):
    """Провайдер зависимостей."""

    bot_config = from_context(provides=BotSettings, scope=Scope.APP)

    site_repo = provide(SitesRepo, scope=Scope.REQUEST, provides=ISitesRepo)
    site_service = provide(SitesService, scope=Scope.REQUEST, provides=ISitesService)



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
