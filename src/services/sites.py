import datetime
import uuid

from src.adapters.api.http.v1.dto.sites import CreateSiteDTO
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo
from src.lib.dto import ArbitraryModel
from src.services.ports.sites import ISitesService


class SitesFilter(ArbitraryModel):
    id: uuid.UUID | None = None
    url: str
    expire_date: datetime.date | None = None


class MassFilter(ArbitraryModel):
    limit: int | None = None
    offset: int | None = None
    ordering: str | None = None


class SitesService(ISitesService):

    def __init__(self, sites: ISitesRepo):
        self.sites = sites

    async def get_site_data(self, filters: SitesFilter):
        return self.sites.get_one(filters)

    async def create_site_data(self, data: CreateSiteDTO):
        return self.sites.create(data)

    async def bulk_create_data(self, bulk_data: list[CreateSiteDTO]):
        return self.sites.bulk_create(bulk_data)

    async def get_sites_list(self, filters: MassFilter):
        return self.sites.get_list(limit=filters.limit, offset=filters.offset, order=filters.ordering)
