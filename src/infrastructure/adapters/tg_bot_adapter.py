from aiogram import Bot

from src.infrastructure.ports.tg_bot_adapter import ITgBotAdapter


class TgBotAdapter(ITgBotAdapter):
    """Адаптер тг-бота."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_messages(self, chat: int, text: str) -> None:
        """Отправка сообщений."""

        await self.bot.send_message(chat, text)
