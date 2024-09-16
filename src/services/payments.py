from abc import ABC

from src.adapters.api.http.v1.dto.payments import PaymentDTO
from src.adapters.spi.persistent.repositories.ports.payments import IPaymentsRepo
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo
from src.services.ports.payments import IPaymentsService


class PaymentsService(IPaymentsService, ABC):

    def __init__(self, sites: ISitesRepo, payments: IPaymentsRepo):
        self.sites = sites
        self.payments = payments

    async def write_down_payment(self, data: PaymentDTO):
        await self.payments.create(data)

