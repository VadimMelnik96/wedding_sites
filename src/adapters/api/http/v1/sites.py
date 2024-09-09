from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get

from src.adapters.api.http.v1.dto.sites import SitesListRequest, SitesDTO
from src.services.ports.sites import ISitesService
from src.services.sites import MassFilter


class WeddingSitesController(Controller):
    path = "/sites"
    tags = ("Сайты",)

    @get(summary="Список сайтов",)
    @inject
    async def list_sites(self, service: FromDishka[ISitesService], query: SitesListRequest) -> list[SitesDTO]:
        return await service.get_sites_list(MassFilter.model_validate(query))

