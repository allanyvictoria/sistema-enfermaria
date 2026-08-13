import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY nao foi encontrada no arquivo .env. "
        "Defina uma chave forte antes de rodar o sistema."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verificar_senha(
    senha: str,
    senha_hash: str
) -> bool:

    return pwd_context.verify(
        senha,
        senha_hash
    )


def gerar_hash_senha(
    senha: str
) -> str:

    return pwd_context.hash(senha)


def criar_token(
    usuario_id: int,
    tipo_acesso: str
) -> str:

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(usuario_id),
        "tipo_acesso": tipo_acesso,
        "exp": expiracao
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )