
from src.adapters.api.http.v1.dto.payments import PaymentDTO
from src.adapters.spi.persistent.models.payments import Payments
from src.adapters.spi.persistent.repositories.ports.payments import IPaymentsRepo
from src.lib.repository import SQLAlchemyRepository




class PaymentsRepo(SQLAlchemyRepository, IPaymentsRepo):
    model = Payments
    response_dto = PaymentDTO
