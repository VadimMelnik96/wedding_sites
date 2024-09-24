from sqlalchemy import select

from src.adapters.api.http.v1.dto.payments import PaymentDTO, PaymentFilter
from src.adapters.spi.persistent.models.payments import Payments
from src.adapters.spi.persistent.repositories.ports.payments import IPaymentsRepo
from src.lib.repository import SQLAlchemyRepository


from src.services.sites import MassFilter


class PaymentsRepo(SQLAlchemyRepository, IPaymentsRepo):
    model = Payments
    response_dto = PaymentDTO

    async def get_payments_list(self, filters: PaymentFilter, mass_filters: MassFilter) -> list[PaymentDTO]:
        stmt = select(self.model)
        filters = filters.model_dump(exclude_unset=True)
        if filters:
            stmt = stmt.filter_by(**filters)
        if mass_filters:
            if mass_filters.ordering:
                stmt = stmt.order_by(mass_filters.ordering)
            if mass_filters.limit:
                stmt = stmt.limit(mass_filters.limit)
            if mass_filters.offset:
                stmt = stmt.offset(mass_filters.offset)
        res = await self._execute(stmt)
        return self.to_dto(res.scalars())
