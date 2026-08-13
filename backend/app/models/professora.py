from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.ocorrencia import Ocorrencia
    from app.models.turma import Turma


class Professora(Base):
    __tablename__ = "professora"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    ativa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    ocorrencias = relationship(
        "Ocorrencia",
        back_populates="professora"
    )

    turmas: Mapped[List[Turma]] = relationship(
        "Turma",
        secondary="turma_professora",
        back_populates="professoras"
    )