import abc


class ITgBotAdapter(abc.ABC):
    """Интерфейс адаптера тг_бота."""

    @abc.abstractmethod
    async def send_message(self,  chat: int, text: str) -> None:
        """Отправка сообщений ботом."""
