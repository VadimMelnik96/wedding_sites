import datetime
import uuid
from dataclasses import dataclass

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


class UpdateSiteDTO(ArbitraryModel):
    expire_date: datetime.date


@dataclass
class SitesListRequest:
    limit: int = 100
    offset: int = 0
    ordering: str = "created_at"
