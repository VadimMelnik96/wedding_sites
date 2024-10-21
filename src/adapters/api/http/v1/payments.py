from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, post, Request, get
from litestar.status_codes import HTTP_200_OK

from src.adapters.api.http.v1.dto.payments import PaymentDTO, PaymentsListRequest, PaymentFilter

from src.services.ports.payments import IPaymentsService
from src.services.sites import MassFilter


class PaymentsController(Controller):
    path = "/payments"
    tags = ("Платежи",)

    @post("/webhooks", summary="Уведомления о платежах")
    @inject
    async def refresh_data_from_yookassa(self, service: FromDishka[IPaymentsService], request: Request) -> HTTP_200_OK:
        event = await request.body()
        await service.handle_update(event)
        return HTTP_200_OK

    @get("/list", summary="Список платежей")
    @inject
    async def get_payments_list(
            self,
            service: FromDishka[IPaymentsService],
            query: PaymentsListRequest
    ) -> list[PaymentDTO]:
        filters = PaymentFilter(site_id=query.site_id, paid=query.paid, status=query.status)
        ordering = MassFilter(ordering=query.ordering, limit=query.limit, offset=query.offset)
        return await service.payment_list(filters, ordering)
