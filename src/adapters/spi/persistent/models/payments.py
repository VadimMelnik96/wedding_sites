from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.spi.persistent.models.base import Base


class Payments(Base):

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(120))
    paid: Mapped[bool] = mapped_column(default=False)
    tg_id: Mapped[int] = mapped_column(default=None, nullable=True)
    amount: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(10))
    confirmation_url: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[str] = mapped_column()
    site: Mapped["Sites"] = relationship(back_populates="payments")
    description: Mapped[str] = mapped_column(String(220))
