from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies.auth import get_escola_id_atual
from app.models.tipo_ocorrencia import TipoOcorrencia
from app.schemas.tipo_ocorrencia import (
    TipoOcorrenciaCreate,
    TipoOcorrenciaResponse
)


router = APIRouter(
    prefix="/tipos-ocorrencia",
    tags=["Tipos de Ocorrência"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[TipoOcorrenciaResponse])
def listar_tipos(
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    return (
        db.query(TipoOcorrencia)
        .filter(TipoOcorrencia.escola_id == escola_id)
        .all()
    )


@router.post(
    "/",
    response_model=TipoOcorrenciaResponse,
    status_code=201
)
def criar_tipo(
    dados: TipoOcorrenciaCreate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    tipo = TipoOcorrencia(**dados.model_dump(), escola_id=escola_id)

    db.add(tipo)
    db.commit()
    db.refresh(tipo)

    return tipo
