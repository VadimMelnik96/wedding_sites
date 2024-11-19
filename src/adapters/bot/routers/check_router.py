import datetime
import uuid
from enum import Enum

import structlog
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.formatting import as_list
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from yookassa import Configuration, Payment

from src.lib.exceptions import NotFoundError
from src.settings.config import config
from src.adapters.api.http.v1.dto.payments import PaymentDTO
from src.adapters.api.http.v1.dto.sites import SitesDTO
from src.services.ports.payments import IPaymentsService
from src.services.ports.sites import ISitesService

check_router = Router()

Configuration.account_id = config.yookassa.shop_id
Configuration.secret_key = config.yookassa.api_key

logger = structlog.get_logger()



class PaymentState(str, Enum):
    check_ttl = "check_t"
    check_payment = "check_p"
    pay = "pay"

class PaymentCallback(CallbackData, prefix="pay"):
    site_id: uuid.UUID | None = None
    payment_id: uuid.UUID | None = None
    url: str | None = None
    action: PaymentState | None = None


@check_router.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"{message.from_user.id} {message.from_user.full_name} начал общение с ботом")
    content = as_list(
        f"Приветствую, {message.from_user.full_name}",
        "Благодарим вас за заказ и использование сайта - приглашения! ",
        "Срок действия сайта - приглашения составляет 1 год со дня вашего мероприятия.",
        "Теперь у вас есть возможность продлить его."
        "Стоимость составляет 490 рублей в год"

    )
    second_text = "Отправьте боту в чат ссылку на ваше общее приглашение, например:\n\n<b>https://proinvite.ru/oscar-maya</b>\n\n<i>*Дополнительные ссылки продлеваются автоматически при продлении общей</i>\n\n<i>**Именные ссылки не подлежат продлению</i>"

    await message.answer(**content.as_kwargs())
    await message.answer(second_text, parse_mode="HTML")



def check_date(expire_date: str) -> str:
    date_object = datetime.datetime.strptime(expire_date, "%Y-%m-%d").date()
    if date_object > datetime.date.today():
        delta = date_object - datetime.date.today()
        return f"Дата окончания поддержки вашего сайта: {date_object}. Осталось {delta.days} дней. Вы можете продлить поддержку на год за 490 рублей"


@check_router.message(F.text)
async def check_ttl(message: types.Message, service: FromDishka[ISitesService]):
    if message.text:
        url = message.text
        logger.info(f"{message.from_user.id} {message.from_user.full_name}: Запрос по сайту {url}")
        try:
            site_data: SitesDTO = await service.get_site_data(url)
            print(site_data)
            answer = check_date(str(site_data.expire_date))
            builder = InlineKeyboardBuilder()
            builder.button(
                text="Продлить поддержку сайта на год",
                callback_data=PaymentCallback(site_id=site_data.id, action=PaymentState.pay)
            )
            builder.button(
                text="Вернуться к проверке ссылок",
                callback_data=PaymentCallback(action=PaymentState.check_ttl)
            )
            await message.answer(answer, reply_markup=builder.as_markup())
            return
        except NotFoundError:
            await message.answer("Такого сайта нет в нашей базе данных. Пожалуйста, проверьте правильность вашей ссылки и введите ее снова")
            return
    await message.answer("Ошибка: не переданы данные")
    return


@check_router.callback_query(PaymentCallback.filter(F.action == PaymentState.check_ttl))
async def another_check_ttl(query: CallbackQuery):
    second_text = "Отправьте боту в чат ссылку на ваше общее приглашение, например:\n\nhttps://proinvite.ru/oscar-maya\n"
    await query.message.edit_text(second_text)
    await query.answer(second_text, parse_mode="HTML")


@check_router.callback_query(PaymentCallback.filter(F.action == PaymentState.pay))
async def get_payment(query: CallbackQuery, callback_data: PaymentCallback, service: FromDishka[IPaymentsService], sites: FromDishka[ISitesService]):

    site_id = callback_data.site_id
    site = await sites.get_site_by_id(site_id)
    payment = Payment.create({
        "amount": {
            "value": 490,
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
        "metadata": {"site_id": str(site_id)},
    })
    confirmation_url = payment.confirmation.confirmation_url
    logger.info(f"Сформирован платеж по сайту {site}")
    payment_dto: PaymentDTO = PaymentDTO(
        id=payment.id,
        site_id=site_id,
        status=payment.status,
        paid=payment.paid,
        tg_id=query.from_user.id,
        amount=str(payment.amount.value),
        currency=payment.amount.currency,
        confirmation_url=confirmation_url,
        created_at=payment.created_at,
        description=payment.description
    )
    await service.write_down_payment(payment_dto)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Я оплатил",
        callback_data=PaymentCallback(payment_id=payment.id, action=PaymentState.check_payment)
    )
    await query.message.edit_text(f"Оплатить: {confirmation_url}", reply_markup=builder.as_markup())
    await query.answer()



@check_router.callback_query(PaymentCallback.filter(F.action == PaymentState.check_payment))
async def check_payment(query: CallbackQuery, callback_data: PaymentCallback, service: FromDishka[IPaymentsService], sites: FromDishka[ISitesService]):
    payment_id = callback_data.payment_id
    payment = await service.get_payment(payment_id)
    site = await sites.get_site_by_id(callback_data.site_id)
    url = site.urls[0]
    if payment.status == "succeeded":
        answer = "Ваш платеж прошел успешно. Поддержка вашего сайта продлена на год"
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Проверить дату истечения",
            callback_data=PaymentCallback(action=PaymentState.check_ttl)
        )
        await (query.message.edit_text(answer, reply_markup=builder.as_markup()))
    elif payment.status == "canceled":
        answer = "Ваш платеж был отклонен платежной системой. Попробуйте снова"
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Повторить попытку",
            callback_data=PaymentCallback(site_id=payment.site_id, action=PaymentState.pay)
        )
        await query.message.edit_text(answer, reply_markup=builder.as_markup())
    else:
        answer = "Ваш платеж ожидает обработки"
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Вернуться к проверке срока",
            callback_data=PaymentCallback(action=PaymentState.check_ttl)
        )
        await query.message.edit_text(answer, reply_markup=builder.as_markup())
        await query.answer()

