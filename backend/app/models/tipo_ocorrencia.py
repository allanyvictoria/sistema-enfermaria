from sqlalchemy import BigInteger, Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoOcorrencia(Base):
    __tablename__ = "tipo_ocorrencia"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # 👈 ADICIONADO
    escola_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("escola.id"), nullable=False)

    nome: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    ocorrencias = relationship(
    "Ocorrencia"
    )
