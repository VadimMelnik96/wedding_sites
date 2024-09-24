import abc

from src.adapters.api.http.v1.dto.payments import PaymentDTO, PaymentFilter
from src.lib.repository import Repository

from src.services.sites import MassFilter


class IPaymentsRepo(Repository):
    """Интерфейс репозитория платежей"""

    @abc.abstractmethod
    async def get_payments_list(self, filters: PaymentFilter, mass_filters: MassFilter) -> list[PaymentDTO]:
        """Метод получения списка платежей"""

