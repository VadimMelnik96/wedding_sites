from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.spi.persistent.models.base import Base, expire_at, created_at, updated_at


class Sites(Base):

    __tablename__ = "sites"

    iid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    url: Mapped[str] = mapped_column(String(120))
    expire_date: Mapped[expire_at]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
