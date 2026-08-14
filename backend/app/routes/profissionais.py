from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies.auth import get_escola_id_atual
from app.models.profissional_enfermagem import ProfissionalEnfermagem
from app.schemas.profissional_enfermagem import (
    ProfissionalEnfermagemCreate,
    ProfissionalEnfermagemResponse
)


router = APIRouter(
    prefix="/profissionais",
    tags=["Profissionais de Enfermagem"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ProfissionalEnfermagemResponse])
def listar_profissionais(
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    return (
        db.query(ProfissionalEnfermagem)
        .filter(ProfissionalEnfermagem.escola_id == escola_id)
        .all()
    )


@router.post(
    "/",
    response_model=ProfissionalEnfermagemResponse,
    status_code=201
)
def criar_profissional(
    dados: ProfissionalEnfermagemCreate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    profissional = ProfissionalEnfermagem(**dados.model_dump(), escola_id=escola_id)

    db.add(profissional)
    db.commit()
    db.refresh(profissional)

    return profissional
