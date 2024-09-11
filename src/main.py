import asyncio
import uvicorn
import uvloop
from aiogram import Bot, Dispatcher
from litestar import Litestar
from litestar.config.compression import CompressionConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka as setup_dishka_for_litestar
from litestar.di import Provide
from dishka.integrations.aiogram import setup_dishka as setup_dishka_for_tg
from settings.config import config, PostgresConfig
from src.adapters.api.http.v1 import v1_router
from src.adapters.bot.routers.check_router import check_router
from src.infrastructure.ioc import ApplicationProvider, PostgresProvider, AiogramProvider
from src.lib.middlewares import DatabaseMiddleware


def get_litestar_app() -> Litestar:
    """Создание экземпляра Litestar приложения."""
    return Litestar(
        path=config.app.root_path,
        route_handlers=[v1_router],
        # plugins=[StructlogPlugin()],
        debug=config.app.debug,
        compression_config=CompressionConfig(backend="gzip", gzip_compress_level=9),
        openapi_config=OpenAPIConfig(
            title=config.openapi.title,
            description=config.openapi.description,
            version="0.0.0",
            render_plugins=[ScalarRenderPlugin()],
            path="/docs",
        ))


def get_app() -> Litestar:
    """Генерация Litestar приложения."""
    litestar_app = get_litestar_app()
    setup_dishka_for_litestar(
        make_async_container(
            ApplicationProvider(),
            PostgresProvider(),
            context={PostgresConfig: config.database}
        ), litestar_app
    )
    # litestar_app.plugins = [StructlogPlugin()]
    litestar_app.middleware = [DatabaseMiddleware]
    return litestar_app

async def get_bot():
    # real main
    bot = Bot(token=config.bot.token.get_secret_value())

    dp = Dispatcher()
    dp.include_router(check_router)

    container = make_async_container(
        ApplicationProvider(),
        AiogramProvider(),
        PostgresProvider(),
        context={PostgresConfig: config.database}
    )
    setup_dishka_for_tg(container=container, router=dp, auto_inject=True)
    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()



app = get_app()


if __name__ == "__main__":
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    asyncio.run(get_bot())
