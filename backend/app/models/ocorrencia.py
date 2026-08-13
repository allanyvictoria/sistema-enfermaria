from datetime import datetime

from sqlalchemy import BigInteger, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Ocorrencia(Base):
    __tablename__ = "ocorrencia"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    aluno_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("aluno.id"),
        nullable=False
    )

    data_hora: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.now
    )

    criado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.now
    )

    professora_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("professora.id"),
        nullable=False
    )

    profissional_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("profissional_enfermagem.id"),
        nullable=False
    )

    usuario_registrou_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("usuario.id"),
        nullable=False
    )

    tipo_ocorrencia_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tipo_ocorrencia.id"),
        nullable=False
    )

    descricao: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    conduta: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    resultado: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )

    responsavel_buscou_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("responsavel.id"),
        nullable=True
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    modificado_em: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True
    )

    # RELACIONAMENTOS

    aluno = relationship(
        "Aluno",
        back_populates="ocorrencias"
    )

    professora = relationship(
        "Professora"
    )

    profissional = relationship(
        "ProfissionalEnfermagem", 
        back_populates="ocorrencias"
    )

    tipo_ocorrencia = relationship(
        "TipoOcorrencia", 
        back_populates="ocorrencias"
    )

    responsavel_buscou = relationship(
        "Responsavel", 
        back_populates="ocorrencias_buscadas"
    )