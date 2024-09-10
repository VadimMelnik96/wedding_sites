from litestar import Router
from src.adapters.api.http.v1.sites import WeddingSitesController

v1_router = Router(path="/v1", route_handlers=[WeddingSitesController])
