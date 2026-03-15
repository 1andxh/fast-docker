from ..db import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
