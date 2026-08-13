from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.aluno import Aluno
    from app.models.turma import Turma


class Matricula(Base):
    __tablename__ = "matricula"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    aluno_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('aluno.id'), nullable=False)

    turma_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('turma.id'), nullable=False)

    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True)

    aluno: Mapped[Aluno] = relationship("Aluno", back_populates="matriculas")
    turma: Mapped[Turma] = relationship("Turma", back_populates="matriculas")