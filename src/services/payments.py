import json
import uuid
from abc import ABC
from datetime import timedelta

from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotificationEventType

from src.adapters.api.http.v1.dto.payments import PaymentDTO, PaymentUpdateDTO, PaymentFilter
from src.adapters.api.http.v1.dto.sites import UpdateSiteDTO
from src.adapters.spi.persistent.repositories.ports.payments import IPaymentsRepo
from src.adapters.spi.persistent.repositories.ports.sites import ISitesRepo

from src.services.ports.payments import IPaymentsService
from src.services.sites import UpdateSitesFilter, MassFilter


class PaymentsService(IPaymentsService, ABC):

    def __init__(self, sites: ISitesRepo, payments: IPaymentsRepo):
        self.sites = sites
        self.payments = payments

    async def write_down_payment(self, data: PaymentDTO):
        """Запись платежа в базе"""
        await self.payments.create(data)

    async def get_payment(self, payment_id: uuid.UUID) -> PaymentDTO:
        """Получение платежа"""
        return await self.payments.get_one(PaymentFilter(id=payment_id))

    async def handle_update(self, event: bytes) -> None:
        """Сценарий обновления данных после успешного платежа"""
        event_json = json.loads(event)
        notification_object = WebhookNotificationFactory().create(event_json)
        response_object = notification_object.object
        payment = await self.payments.get_one(PaymentFilter(id=response_object.id))
        await self.payments.update(
            PaymentUpdateDTO(status=response_object.status, paid=response_object.paid),
            PaymentFilter(id=payment.id)
        )
        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            site = await self.sites.get_one(UpdateSitesFilter(id=payment.site_id))
            update_data = UpdateSiteDTO(expire_date=site.expire_date + timedelta(days=365))
            await self.sites.update(update_data, UpdateSitesFilter(id=payment.site_id))

    async def payment_list(self, filters: PaymentFilter, mass_filter: MassFilter) -> list[PaymentDTO]:
        """Сценарий получения списка платежей"""
        return await self.payments.get_list(filters=filters, order_filters=mass_filter)

# тело тестового уведомления о успешной оплате продления

# {
#   "type": "notification",
#   "event": "payment.succeeded",
#   "object": {
#     "id": "2e794bdb-000f-5000-9000-1f02b3337f03",
#     "status": "succeeded",
#     "paid": true,
#     "amount": {
#       "value": "2.00",
#       "currency": "RUB"
#     },
#     "authorization_details": {
#       "rrn": "10000000000",
#       "auth_code": "000000",
#       "three_d_secure": {
#         "applied": true
#       }
#     },
#     "created_at": "2018-07-10T14:27:54.691Z",
#     "description": "Заказ №72",
#     "expires_at": "2018-07-17T14:28:32.484Z",
#     "metadata": {},
#     "payment_method": {
#       "type": "bank_card",
#       "id": "2e794bdb-000f-5000-9000-1f02b3337f03",
#       "saved": false,
#       "card": {
#         "first6": "555555",
#         "last4": "4444",
#         "expiry_month": "07",
#         "expiry_year": "2021",
#         "card_type": "MasterCard",
#       "issuer_country": "RU",
#       "issuer_name": "Sberbank"
#       },
#       "title": "Bank card *4444"
#     },
#     "refundable": false,
#     "test": false
#   }
# }
