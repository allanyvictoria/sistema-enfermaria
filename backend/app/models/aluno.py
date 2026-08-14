from __future__ import annotations
from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import BigInteger, Boolean, Date, Text, String, TIMESTAMP, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# Imports apenas para verificação de tipos (evita import circular)
if TYPE_CHECKING:
    from app.models.responsavel import Responsavel
    from app.models.ocorrencia import Ocorrencia
    from app.models.matricula import Matricula

# Tabela intermediária de ligação (Aluno <-> Responsável)
aluno_responsavel = Table(
    'aluno_responsavel',
    Base.metadata,
    Column('aluno_id', BigInteger, ForeignKey('aluno.id', ondelete="CASCADE"), primary_key=True),
    Column('responsavel_id', BigInteger, ForeignKey('responsavel.id', ondelete="CASCADE"), primary_key=True)
)


class Aluno(Base):
    __tablename__ = "aluno"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    # 👈 ADICIONADO
    escola_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("escola.id"),
        nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    data_nascimento: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    foto_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    observacoes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # 📌 Colunas de Texto Simples (para o cadastro direto do formulário)
    alergias: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    condicoes_saude: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.now
    )

    # 📌 Relacionamentos
    ocorrencias: Mapped[List[Ocorrencia]] = relationship(
        "Ocorrencia",
        back_populates="aluno"
    )

    responsaveis: Mapped[List[Responsavel]] = relationship(
        "Responsavel",
        secondary=aluno_responsavel,
        back_populates="alunos"
    )

    matriculas: Mapped[List[Matricula]] = relationship(
        "Matricula",
        back_populates="aluno"
    )

    # 📌 Propriedades calculadas
    @property
    def turma_id(self) -> int | None:
        # Retorna a turma da matrícula ativa (data_fim is None) se existir
        for m in self.matriculas:
            if m.data_fim is None:
                return m.turma_id
        return None

    @property
    def turma(self):
        # Retorna o objeto Turma associado à matrícula ativa, se existir
        for m in self.matriculas:
            if m.data_fim is None and getattr(m, 'turma', None) is not None:
                return m.turma
        return None
