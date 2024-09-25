import uuid
from dataclasses import dataclass

from src.lib.dto import ArbitraryModel


class PaymentDTO(ArbitraryModel):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: str
    status: str
    paid: bool
    amount: str
    currency: str
    confirmation_url: str
    description: str


class PaymentUpdateDTO(ArbitraryModel):
    status: str
    paid: bool


@dataclass
class PaymentsListRequest:
    id: uuid.UUID | None
    site_id: uuid.UUID | None
    status: str | None
    paid: bool | None
    limit: int | None = 0
    offset: int | None = 100
    ordering: str | None = None


class PaymentFilter(ArbitraryModel):
    id: uuid.UUID | None
    site_id: uuid.UUID | None
    status: str | None
    paid: bool | None
