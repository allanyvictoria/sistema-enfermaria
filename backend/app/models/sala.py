from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Sala(Base):
    __tablename__ = "sala"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    descricao: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    ativa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )