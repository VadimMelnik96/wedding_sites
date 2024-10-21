from sqlalchemy import select, any_

from src.adapters.api.http.v1.dto.sites import SitesDTO
from src.adapters.spi.persistent.models.sites import Sites
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo
from src.lib.repository import SQLAlchemyRepository


class SitesRepo(SQLAlchemyRepository, ISitesRepo):
    model = Sites
    response_dto = SitesDTO

    async def get_site_by_url(self, url: str) -> SitesDTO:
        stmt = select(Sites).where(url == any_(Sites.urls))
        res = await self._execute(stmt)

        instance = res.scalar_one_or_none()

        self.check_not_found(instance)
        return self.to_dto(instance, self.response_dto)

