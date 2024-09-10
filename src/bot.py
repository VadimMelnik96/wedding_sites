import asyncio
import time
import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.formatting import as_list

from settings.config import config

bot = Bot(token=config.bot.token.get_secret_value())

dp = Dispatcher()

todays = datetime.date.fromtimestamp(time.time())

fake_db = {
    "https://nikita.com": "2025-06-12",
    "https://prosrocheno.com": "2023-06-12",
}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    content = as_list(
        f"Привет, {message.from_user.full_name}",
        "Этот бот поможет тебе узнать, сколько еще осталось жить твоему сайту. "
        "Пожалуйста, введи ссылку на твой сайт"
    )
    await message.answer(**content.as_kwargs())


def check_date(url: str) -> str:
    expire_date = fake_db.get(url)
    if expire_date:
        date_object = datetime.datetime.strptime(expire_date, "%Y-%m-%d").date()
        if date_object > datetime.date.today():
            delta = date_object - datetime.date.today()
            return f"Дата окончания поддержки вашего сайта: {expire_date}. Осталось {delta.days} дней."
        return f"Ваш сайт больше не поддерживается"
    return f"Такого сайта нет в нашей базе. Пожалуйста, проверьте правильность введенных данных"


@dp.message(F.text)
async def check_ttl(message: types.Message):
    if message.text:

        url = message.text
        answer = check_date(url)
        await message.answer(answer)
        return
    await message.answer("Ошибка: не переданы данные")
    return


async def main():
    await dp.start_polling(bot)

