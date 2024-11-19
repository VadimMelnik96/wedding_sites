from typing import AsyncIterator

from aiogram.types import TelegramObject
from dishka import Provider, from_context, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.tg_bot_adapter import TgBotAdapter
from src.infrastructure.ports.tg_bot_adapter import ITgBotAdapter
from src.settings.config import PostgresConfig, BotSettings
from src.adapters.spi.persistent.repositories.payments_repo import PaymentsRepo
from src.adapters.spi.persistent.repositories.ports.payments import IPaymentsRepo
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo
from src.adapters.spi.persistent.repositories.sites_repo import SitesRepo
from src.lib.database import Database
from src.services.payments import PaymentsService
from src.services.ports.payments import IPaymentsService
from src.services.ports.sites import ISitesService
from src.services.sites import SitesService


class ApplicationProvider(Provider):
    """Провайдер зависимостей."""

    bot_config = from_context(provides=BotSettings, scope=Scope.APP)
    bot_adapter = provide(TgBotAdapter, scope=Scope.APP, provides=ITgBotAdapter)
    site_repo = provide(SitesRepo, scope=Scope.REQUEST, provides=ISitesRepo)
    payments_repo = provide(PaymentsRepo, scope=Scope.REQUEST, provides=IPaymentsRepo)
    site_service = provide(SitesService, scope=Scope.REQUEST, provides=ISitesService)
    payments_service = provide(PaymentsService, scope=Scope.REQUEST, provides=IPaymentsService)
