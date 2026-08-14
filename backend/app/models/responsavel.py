from sqlalchemy import BigInteger, Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Responsavel(Base):
    __tablename__ = "responsavel"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # 👈 ADICIONADO (correção pós-Etapa 1 — ver migracao_responsavel_escola.sql)
    escola_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("escola.id"), nullable=False)

    nome: Mapped[str] = mapped_column(String(150), nullable=False)

    parentesco: Mapped[str] = mapped_column(String(50), nullable=False)

    telefone_principal: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    telefone_secundario: Mapped[str | None] = mapped_column(String(20))

    email: Mapped[str | None] = mapped_column(String(150))

    autorizado_buscar: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    ocorrencias_buscadas = relationship(
        "Ocorrencia", 
        back_populates="responsavel_buscou"
    )

    alunos = relationship(
        "Aluno",
        secondary="aluno_responsavel",
        back_populates="responsaveis"
    )
