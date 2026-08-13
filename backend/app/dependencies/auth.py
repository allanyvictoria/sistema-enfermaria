from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.auth.security import ALGORITHM, SECRET_KEY
from app.database import SessionLocal
from app.models.usuario import Usuario

security = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente ou inválido.",
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sem usuário válido.",
        )

    usuario = db.get(Usuario, int(usuario_id))
    if usuario is None or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido ou inativo.",
        )

    return usuario


def requer_perfil(*perfis: str) -> Callable[[Usuario], Usuario]:
    def dependencia(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.tipo_acesso not in perfis:
            perfis_texto = ", ".join(perfis)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Permissão necessária: {perfis_texto}.",
            )
        return usuario

    return dependencia


somente_admin = requer_perfil("ADMIN")
somente_enfermagem = requer_perfil("ENFERMAGEM")
admin_ou_enfermagem = requer_perfil("ADMIN", "ENFERMAGEM")
qualquer_usuario = requer_perfil("ADMIN", "ENFERMAGEM", "PROFESSORA")
