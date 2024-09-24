import json
from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get, post, Request, Response
from litestar.status_codes import HTTP_200_OK
from src.adapters.api.http.v1.dto.sites import SitesListRequest, SitesDTO, CreateSiteDTO
from src.services.ports.payments import IPaymentsService
from src.services.ports.sites import ISitesService
from src.services.sites import MassFilter, SitesFilter


class WeddingSitesController(Controller):
    path = "/sites"
    tags = ("Сайты",)

    @get("/list", summary="Список сайтов",)
    @inject
    async def list_sites(self, service: FromDishka[ISitesService], query: SitesListRequest) -> list[SitesDTO]:
        return await service.get_sites_list(MassFilter.model_validate(query.__dict__))

    @post(summary="Добавить сайт")
    @inject
    async def create_site(self, service: FromDishka[ISitesService], data: CreateSiteDTO) -> SitesDTO:
        return await service.create_site_data(data=data)

    @post("/many", summary="Добавить несколько сайтов")
    @inject
    async def bulk_create(self, service: FromDishka[ISitesService], data: list[CreateSiteDTO]) -> list[SitesDTO]:
        return await service.bulk_create_data(bulk_data=data)

    @post("/get_site", summary="Найти сайт")
    @inject
    async def get_site(self, service: FromDishka[ISitesService], data: SitesFilter) -> SitesDTO:
        return await service.get_site_data(data)

    @post("/webhooks", summary="Уведомления о платежах")
    @inject
    async def refresh_data_from_yookassa(self, service: FromDishka[IPaymentsService], request: Request) -> HTTP_200_OK:
        event = await request.body()
        await service.handle_update(event)
        return HTTP_200_OK


    # TODO роутер платежей, пересмотреть методы в этом роутере по REST
    # TODO логгинг
