import abc
import uuid


class ISitesService(abc.ABC):

    @abc.abstractmethod
    async def get_site_data(self, url: str):
        """Метод получения данных сайта"""

    @abc.abstractmethod
    async def get_site_by_id(self, site_id: uuid.UUID):
        """Метод получения данных по id"""

    @abc.abstractmethod
    async def get_sites_list(self, sites_filters, listing_filters):
        """Метод получения списка сайтов"""

    @abc.abstractmethod
    async def create_site_data(self, data):
        """Метод создания данных о сайте"""

    @abc.abstractmethod
    async def bulk_create_data(self, bulk_data):
        """Метод массового добавления данных о сайтах"""
