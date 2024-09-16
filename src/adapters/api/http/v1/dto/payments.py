import uuid
import datetime

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
