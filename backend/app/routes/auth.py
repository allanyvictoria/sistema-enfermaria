from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.dependencies.auth import get_usuario_atual

from app.schemas.auth import (
    LoginRequest,
    LoginResponse
)

from app.auth.security import (
    verificar_senha,
    criar_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.login == dados.login,
            Usuario.escola_id == dados.escola_id,
            Usuario.ativo == True
        )
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Login ou senha inválidos"
        )

    if not verificar_senha(
        dados.senha,
        usuario.senha_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Login ou senha inválidos"
        )

    token = criar_token(
        usuario.id,
        usuario.tipo_acesso,
        usuario.escola_id
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
        "tipo_acesso": usuario.tipo_acesso,
        "escola_id": usuario.escola_id
    }

@router.get("/me")
def obter_usuario_logado(usuario: Usuario = Depends(get_usuario_atual)):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "login": usuario.login,
        "tipo_acesso": usuario.tipo_acesso,
        "escola_id": usuario.escola_id
    }