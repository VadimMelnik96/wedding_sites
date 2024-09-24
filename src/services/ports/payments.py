import abc

from src.adapters.api.http.v1.dto.payments import PaymentDTO, PaymentFilter

from src.services.sites import MassFilter


class IPaymentsService(abc.ABC):

    @abc.abstractmethod
    async def write_down_payment(self, data):
        """Метод создания записи о платеже"""

    @abc.abstractmethod
    async def handle_update(self, event: bytes):
        """Метод обработки уведомлений Юкассы"""

    @abc.abstractmethod
    async def payment_list(self, filters: PaymentFilter, mass_filter: MassFilter) -> list[PaymentDTO]:
        """Метод получения списка платежей"""
        