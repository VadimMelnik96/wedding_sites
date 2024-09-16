import datetime
import json

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.formatting import as_list
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from dishka.integrations.aiogram import inject
from yookassa import Configuration, Payment

from settings.config import config
from src.adapters.api.http.v1.dto.payments import PaymentDTO
from src.adapters.api.http.v1.dto.sites import SitesDTO
from src.services.ports.payments import IPaymentsService
from src.services.ports.sites import ISitesService
from src.services.sites import SitesFilter

check_router = Router()

Configuration.account_id = config.yookassa.shop_id
Configuration.secret_key = config.yookassa.api_key

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
            return f"Дата окончания поддержки вашего сайта: {expire_date}. Осталось {delta.days} дней. Вы можете продлить поддержку на год за 390 рублей"


@check_router.message(F.text)
async def check_ttl(message: types.Message, service: FromDishka[ISitesService]):

    if message.text:
        url = message.text
        site_data: SitesDTO = await service.get_site_data(SitesFilter(url=url))
        answer = check_date(str(site_data.expire_date))
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Продлить поддержку сайта на год",
            callback_data=f"year_{str(site_data.id)}_{site_data.url})"
        ))
        await message.answer(answer, reply_markup=builder.as_markup())
        return
    await message.answer("Ошибка: не переданы данные")
    return

@check_router.callback_query(F.data.startswith("year_"))
async def get_payment(callback: types.CallbackQuery, service: FromDishka[IPaymentsService]):
    site_id, site = callback.data.split("_")[1], callback.data.split("_")[2].replace(")", "")
    payment = Payment.create({
        "amount": {
            "value": 390,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "http://t.me/test_check_wedding_bot"
        },
        "capture": True,
        "description": f"Продление обслуживания сайта {site} на 1 год",
        "metadata" : {"site_id": site_id},
        })
    confirmation_url = payment.confirmation.confirmation_url

    payment_dto: PaymentDTO = PaymentDTO(
        id=payment.id,
        site_id=site_id,
        status=payment.status,
        paid=payment.paid,
        amount=str(payment.amount.value),
        currency=payment.amount.currency,
        confirmation_url=confirmation_url,
        created_at=payment.created_at,
        description=payment.description
    )
    await service.write_down_payment(payment_dto)
    await callback.message.edit_text(f"Перейдите по ссылке для оплаты: {confirmation_url}")
    await callback.answer()

