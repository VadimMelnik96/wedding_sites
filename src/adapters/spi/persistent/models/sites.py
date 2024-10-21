from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.spi.persistent.models.base import Base, expire_at, created_at, updated_at


class Sites(Base):

    __tablename__ = "sites"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    urls: Mapped[List[str]] = mapped_column(ARRAY(String), unique=True, nullable=False, index=True)
    payments: Mapped[Optional[List["Payments"]]] = relationship(back_populates="site")
    expire_date: Mapped[expire_at]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
