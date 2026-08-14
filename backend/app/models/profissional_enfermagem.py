from sqlalchemy import BigInteger, Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProfissionalEnfermagem(Base):
    __tablename__ = "profissional_enfermagem"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # 👈 ADICIONADO
    escola_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("escola.id"), nullable=False)

    nome: Mapped[str] = mapped_column(String(150), nullable=False)

    funcao: Mapped[str] = mapped_column(String(20), nullable=False)

    registro_coren: Mapped[str | None] = mapped_column(String(30))

    telefone: Mapped[str | None] = mapped_column(String(20))

    ativa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    ocorrencias = relationship(
        "Ocorrencia", 
        back_populates="profissional"
    )
