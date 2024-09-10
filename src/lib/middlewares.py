from litestar.middleware import MiddlewareProtocol

from src.lib.database import Database

try:
    from litestar.types import ASGIApp, Receive, Scope, Send
except ImportError as exc:
    EXCEPTION_MESSAGE = "Необходимо установить litestar"
    raise ImportError(EXCEPTION_MESSAGE) from exc


class DatabaseMiddleware(MiddlewareProtocol):
    """Промежуточный слой для открытия scoped session на запросах."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Открытие scoped session."""
        if scope["type"] == "http":
            container = scope["app"].state.dishka_container
            database = await container.get(Database)
            async with database.database_scope():
                await self.app(scope, receive, send)
        await self.app(scope, receive, send)