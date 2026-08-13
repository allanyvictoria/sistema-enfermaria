from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import BigInteger, Boolean, String, SmallInteger, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.professora import Professora
    from app.models.matricula import Matricula


# Tabela de associação Turma <-> Professora
turma_professora = Table(
    'turma_professora',
    Base.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('turma_id', BigInteger, ForeignKey('turma.id', ondelete='CASCADE')),
    Column('professora_id', BigInteger, ForeignKey('professora.id', ondelete='CASCADE')),
    Column('papel', String(20), nullable=True)
)


class Turma(Base):
    __tablename__ = "turma"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    sala_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('sala.id'), nullable=False)
    turno: Mapped[str] = mapped_column(String(10), nullable=False)
    ano_letivo: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    professoras: Mapped[List[Professora]] = relationship(
        "Professora",
        secondary=turma_professora,
        back_populates="turmas"
    )

    matriculas: Mapped[List[Matricula]] = relationship(
        "Matricula",
        back_populates="turma"
    )