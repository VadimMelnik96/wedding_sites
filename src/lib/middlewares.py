from litestar.middleware import MiddlewareProtocol

from src.lib.database import Database

try:
    from litestar.types import ASGIApp, Receive, Scope, Send
except ImportError as exc:
    EXCEPTION_MESSAGE = "Необходимо установить litestar"
    raise ImportError(EXCEPTION_MESSAGE) from exc

def db_middleware_factory(app: ASGIApp) -> ASGIApp:
    """Фабрика промежуточного слоя."""
    async def db_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        container = scope["app"].state.dishka_container
        database = await container.get(Database)
        async with database.database_scope():
            await app(scope, receive, send)

    return db_middleware

