from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.escola import Escola
from app.schemas.escola import EscolaResponse


router = APIRouter(
    prefix="/escolas",
    tags=["Escolas"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "",
    response_model=list[EscolaResponse]
)
def listar_escolas(db: Session = Depends(get_db)):
    """
    Rota pública (sem autenticação) — usada pela tela de login
    pra popular a lista de escolas antes do usuário se identificar.
    """
    return (
        db.query(Escola)
        .filter(Escola.ativa == True)
        .order_by(Escola.nome)
        .all()
    )
