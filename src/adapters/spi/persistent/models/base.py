import datetime

from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, mapped_column


created_at = Annotated[datetime.datetime, mapped_column(default=datetime.datetime.now())]
updated_at = Annotated[datetime.datetime, mapped_column(
    default=datetime.datetime.now(),
    onupdate=datetime.datetime.now
)]
expire_at = Annotated[datetime.date, mapped_column()]


class Base(DeclarativeBase):
    pass
