from datetime import datetime
from sqlalchemy import BigInteger, Boolean, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    # 👈 ADICIONADO: cada usuário pertence a uma escola
    escola_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("escola.id"),
        nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    # login não é mais globalmente único — só dentro da mesma escola
    # (a unicidade combinada é garantida pelo índice único no banco:
    # idx_usuario_login_escola)
    login: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    senha_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    tipo_acesso: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ADMIN"
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
