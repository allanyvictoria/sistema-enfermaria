from datetime import datetime
from sqlalchemy import BigInteger, Boolean, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Escola(Base):
    __tablename__ = "escola"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    ativa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.now
    )
