import datetime
import uuid
from dataclasses import dataclass

from src.lib.dto import ArbitraryModel


class SitesDTO(ArbitraryModel):
    id: uuid.UUID
    urls: list[str]
    expire_date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CreateSiteDTO(ArbitraryModel):
    urls: list[str]
    expire_date: datetime.date


class UpdateSiteDTO(ArbitraryModel):
    expire_date: datetime.date


@dataclass
class SitesListRequest:
    url: str | None = None
    id: uuid.UUID | None = None
    limit: int | None = 100
    offset: int | None = 0
    ordering: str | None = "created_at"


@dataclass
class SitesRequest:
    url: str | None = None
    id: uuid.UUID | None = None
