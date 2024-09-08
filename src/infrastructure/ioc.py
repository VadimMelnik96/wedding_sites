from dishka import Provider, from_context, Scope

from settings.config import PostgresConfig, BotSettings


class ApplicationProvider(Provider):
    """Провайдер зависимостей."""

    postgres_config = from_context(provides=PostgresConfig, scope=Scope.APP)
    bot_config = from_context(provides=BotSettings, scope=Scope.APP)

