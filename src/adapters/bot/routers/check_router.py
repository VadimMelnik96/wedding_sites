import datetime
import uuid

import structlog
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.formatting import as_list, Bold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from yookassa import Configuration, Payment

from src.lib.exceptions import NotFoundError
from src.services.payments import PaymentsService
from src.settings.config import config
from src.adapters.api.http.v1.dto.payments import PaymentDTO
from src.adapters.api.http.v1.dto.sites import SitesDTO
from src.services.ports.payments import IPaymentsService
from src.services.ports.sites import ISitesService
from src.services.sites import SitesFilter

check_router = Router()

Configuration.account_id = config.yookassa.shop_id
Configuration.secret_key = config.yookassa.api_key

logger = structlog.get_logger()


@check_router.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"{message.from_user.id} {message.from_user.full_name} начал общение с ботом")
    content = as_list(
        f"Приветствую, {message.from_user.full_name}",
        "Благодарим вас за заказ и использование сайта - приглашения! ",
        "Со дня вашего мероприятия ваш сайт по умолчанию будет существовать год.",
        "Теперь у вас есть возможность продлить это время за 390 рублей в год."

    )
    second_text = f"Отправьте боту в чат ссылку на ваше общее приглашение, например:\n\n<b>https://proinvite\.ru/oscar-maya</b>\n\n<i>*Дополнительные ссылки продлеваются автоматически при продлении общей</i>\n\n<i>**Именные ссылки не подлежат продлению</i>"

    await message.answer(**content.as_kwargs())
    await message.answer(second_text, parse_mode="HTML")


def check_date(expire_date: str) -> str:
    date_object = datetime.datetime.strptime(expire_date, "%Y-%m-%d").date()
    if date_object > datetime.date.today():
        delta = date_object - datetime.date.today()
        return f"Дата окончания поддержки вашего сайта: {expire_date}. Осталось {delta.days} дней. Вы можете продлить поддержку на год за 390 рублей"


@check_router.message(F.text)
async def check_ttl(message: types.Message, service: FromDishka[ISitesService]):
    if message.text:
        url = message.text
        logger.info(f"{message.from_user.id} {message.from_user.full_name}: Запрос по сайту {url}")
        try:
            site_data: SitesDTO = await service.get_site_data(SitesFilter(url=url))
            answer = check_date(str(site_data.expire_date))
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Продлить поддержку сайта на год",
                callback_data=f"year_{str(site_data.id)}_{site_data.url})"
            ))
            await message.answer(answer, reply_markup=builder.as_markup())
        except NotFoundError:
            await message.answer("Такого сайта нет в нашей базе данных. Пожалуйста, проверьте правильность вашей ссылки и введите ее снова")
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
        "metadata": {"site_id": site_id},
    })
    confirmation_url = payment.confirmation.confirmation_url
    logger.info(f"Сформирован платеж по сайту {site}")
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
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Проверить статус платежа",
        callback_data=f"сh_payment.{payment.id})"
    ))
    await callback.message.edit_text(f"Для продления вашего сайта {site} перейдите по ссылке для оплаты: {confirmation_url}", reply_markup=builder.as_markup())
    await callback.answer()



@check_router.callback_query(F.data.startswith("ch_payment"))
async def check_payment(callback: types.CallbackQuery, service: FromDishka[IPaymentsService]):

    payment_id = uuid.UUID(callback.data.split(".")[1])
    payment = await service.get_payment(payment_id)
    if payment.status == "succeeded":
        answer = "Ваш платеж прошел успешно. Поддержка вашего сайта продлена на год"
    elif payment.status == "canceled":
        answer = "Ваш платеж был отклонен платежной системой. Попробуйте снова"
    else:
        answer = "Ваш платеж ожидает обработки"
    await callback.message.edit_text(answer)
