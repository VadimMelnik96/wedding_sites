import uuid
from dataclasses import dataclass

from src.lib.dto import ArbitraryModel


class PaymentDTO(ArbitraryModel):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: str
    status: str
    paid: bool
    tg_id: int
    amount: str
    currency: str
    confirmation_url: str
    description: str


class PaymentUpdateDTO(ArbitraryModel):
    status: str
    paid: bool


@dataclass
class PaymentsListRequest:
    site_id: uuid.UUID | None = None
    status: str | None = None
    paid: bool | None = None
    limit: int | None = 100
    offset: int | None = 0
    ordering: str | None = None


class PaymentFilter(ArbitraryModel):
    id: uuid.UUID | None = None
    site_id: uuid.UUID | None = None
    status: str | None = None
    paid: bool | None = None
