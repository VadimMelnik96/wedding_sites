import abc

from src.adapters.api.http.v1.dto.sites import SitesDTO
from src.lib.repository import Repository


class ISitesRepo(Repository):
    """Интерфейс репозитория сайтов"""

    @abc.abstractmethod
    async def get_site_by_url(self, url: str) -> SitesDTO:
        """Метод получения записи по одной ссылке"""