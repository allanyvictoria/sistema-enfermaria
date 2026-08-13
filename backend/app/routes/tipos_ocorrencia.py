from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
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
def listar_tipos(db: Session = Depends(get_db)):
    return db.query(TipoOcorrencia).all()


@router.post(
    "/",
    response_model=TipoOcorrenciaResponse,
    status_code=201
)
def criar_tipo(
    dados: TipoOcorrenciaCreate,
    db: Session = Depends(get_db)
):
    tipo = TipoOcorrencia(**dados.model_dump())

    db.add(tipo)
    db.commit()
    db.refresh(tipo)

    return tipo