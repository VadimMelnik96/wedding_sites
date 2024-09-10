import datetime

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.formatting import as_list
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.adapters.api.http.v1.dto.sites import SitesDTO
from src.services.ports.sites import ISitesService
from src.services.sites import SitesFilter

check_router = Router()


@check_router.message(Command("start"))
async def cmd_start(message: types.Message):
    content = as_list(
        f"Привет, {message.from_user.full_name}",
        "Этот бот поможет тебе узнать, сколько еще осталось жить твоему сайту. "
        "Пожалуйста, введи ссылку на твой сайт"
    )
    await message.answer(**content.as_kwargs())


def check_date(expire_date: str) -> str:
        date_object = datetime.datetime.strptime(expire_date, "%Y-%m-%d").date()
        if date_object > datetime.date.today():
            delta = date_object - datetime.date.today()
            return f"Дата окончания поддержки вашего сайта: {expire_date}. Осталось {delta.days} дней."


@check_router.message(F.text)
async def check_ttl(message: types.Message, service: FromDishka[ISitesService]):

    if message.text:
        url = message.text
        site_data: SitesDTO = await service.get_site_data(SitesFilter(url=url))
        print(site_data)
        answer = check_date(str(site_data.expire_date))
        await message.answer(answer)
        return
    await message.answer("Ошибка: не переданы данные")
    return
