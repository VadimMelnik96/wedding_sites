import datetime
import uuid

from src.lib.dto import ArbitraryModel


class SitesDTO(ArbitraryModel):
    id: uuid.UUID
    url: str
    expire_date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CreateSiteDTO(ArbitraryModel):
    url: str
    expire_date: datetime.date

