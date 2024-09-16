import abc


class IPaymentsService(abc.ABC):

    @abc.abstractmethod
    async def write_down_payment(self, data):
        """Метод создания записи о платеже"""