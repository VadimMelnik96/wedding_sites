from dishka import Provider, from_context, Scope, provide

from settings.config import PostgresConfig, BotSettings
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo
from src.adapters.spi.persistent.repositories.sites_repo import SitesRepo
from src.lib.database import Database
from src.lib.providers import get_session
from src.services.ports.sites import ISitesService
from src.services.sites import SitesService


class ApplicationProvider(Provider):
    """Провайдер зависимостей."""

    postgres_config = from_context(provides=PostgresConfig, scope=Scope.APP)
    bot_config = from_context(provides=BotSettings, scope=Scope.APP)
    database = provide(Database, scope=Scope.APP)
    session = provide(get_session, scope=Scope.REQUEST)
    site_repo = provide(SitesRepo, scope=Scope.REQUEST, provides=ISitesRepo)
    site_service = provide(SitesService, scope=Scope.REQUEST, provides=ISitesService)
