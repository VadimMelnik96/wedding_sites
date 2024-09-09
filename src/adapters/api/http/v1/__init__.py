from litestar import Router, Litestar

import settings
from src.adapters.api.http.v1.sites import WeddingSitesController

v1_router = Router(path="/v1", route_handlers=[WeddingSitesController])



def get_litestar_app() -> Litestar:
    """Создание экземпляра Litestar приложения."""
    return Litestar(
        path=settings.app.root_path,
        route_handlers=[v1_router],
        # plugins=[StructlogPlugin()],
        debug=settings.app.debug,
        compression_config=CompressionConfig(backend="gzip", gzip_compress_level=9),
        openapi_config=OpenAPIConfig(
            title=settings.openapi.title,
            description=settings.openapi.description,
            version="0.0.0",
            render_plugins=[ScalarRenderPlugin()],
            path="/docs",
        ),