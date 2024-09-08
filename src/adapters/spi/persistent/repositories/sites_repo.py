from src.adapters.api.http.v1.dto.sites import SitesDTO
from src.adapters.spi.persistent.models.sites import Sites
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo
from src.lib.repository import SQLAlchemyRepository


class SitesRepo(SQLAlchemyRepository, ISitesRepo):
    model = Sites
    response_dto = SitesDTO
