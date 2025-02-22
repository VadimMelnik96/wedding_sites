
from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get, post
from litestar.exceptions import HTTPException

from src.adapters.api.http.v1.dto.sites import SitesListRequest, SitesDTO, CreateSiteDTO
from src.lib.exceptions import NotFoundError
from src.services.ports.sites import ISitesService
from src.services.sites import MassFilter, SitesFilter


class WeddingSitesController(Controller):
    path = "/sites"
    tags = ("Сайты",)

    @get("/list", summary="Список сайтов",)
    @inject
    async def list_sites(self, service: FromDishka[ISitesService], query: SitesListRequest) -> list[SitesDTO]:
        sites_filter = SitesFilter(id=query.id, url=query.url)
        listing = MassFilter(limit=query.limit, offset=query.offset, ordering=query.ordering)
        return await service.get_sites_list(sites_filter, listing)

    @post(summary="Добавить сайт")
    @inject
    async def create_site(self, service: FromDishka[ISitesService], data: CreateSiteDTO) -> SitesDTO:
        return await service.create_site_data(data=data)

    @post("/many", summary="Добавить несколько сайтов")
    @inject
    async def bulk_create(self, service: FromDishka[ISitesService], data: list[CreateSiteDTO]) -> list[SitesDTO]:
        return await service.bulk_create_data(bulk_data=data)

    @get("/get_site/{url:str}", summary="Найти сайт")
    @inject
    async def get_site(self, service: FromDishka[ISitesService], url: str) -> SitesDTO:
        try:
            return await service.get_site_data(url)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail="Сайт не найден") from exc

