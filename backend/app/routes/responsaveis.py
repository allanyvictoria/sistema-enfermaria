from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.dependencies.auth import admin_ou_enfermagem, qualquer_usuario
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.schemas.responsavel import (
    ResponsavelCreate,
    ResponsavelResponse,
    ResponsavelDetailResponse,
)


router = APIRouter(
    prefix="/responsaveis",
    tags=["Responsáveis"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ResponsavelDetailResponse],
    dependencies=[Depends(qualquer_usuario)],
)
def listar_responsaveis(db: Session = Depends(get_db)):
    # joinedload traz os alunos vinculados junto, evitando N+1 queries
    return (
        db.query(Responsavel)
        .options(joinedload(Responsavel.alunos))
        .all()
    )


@router.get(
    "/{responsavel_id}",
    response_model=ResponsavelDetailResponse,
    dependencies=[Depends(qualquer_usuario)],
)
def buscar_responsavel(responsavel_id: int, db: Session = Depends(get_db)):
    responsavel = (
        db.query(Responsavel)
        .options(joinedload(Responsavel.alunos))
        .filter(Responsavel.id == responsavel_id)
        .first()
    )

    if not responsavel:
        raise HTTPException(status_code=404, detail="Responsável não encontrado")

    return responsavel


@router.post("/", response_model=ResponsavelResponse, status_code=201)
def criar_responsavel(
    dados: ResponsavelCreate,
    db: Session = Depends(get_db)
):
    responsavel = Responsavel(**dados.model_dump())

    db.add(responsavel)
    db.commit()
    db.refresh(responsavel)

    return responsavel


# ==========================================
# Vínculo Responsável <-> Aluno 
# ==========================================
@router.post(
    "/{responsavel_id}/vincular/{aluno_id}",
    response_model=ResponsavelDetailResponse,
    dependencies=[Depends(admin_ou_enfermagem)],
)
def vincular_aluno(responsavel_id: int, aluno_id: int, db: Session = Depends(get_db)):
    responsavel = (
        db.query(Responsavel)
        .options(joinedload(Responsavel.alunos))
        .filter(Responsavel.id == responsavel_id)
        .first()
    )
    if not responsavel:
        raise HTTPException(status_code=404, detail="Responsável não encontrado")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    if aluno not in responsavel.alunos:
        responsavel.alunos.append(aluno)
        db.commit()
        db.refresh(responsavel)

    return responsavel


@router.delete(
    "/{responsavel_id}/vincular/{aluno_id}",
    response_model=ResponsavelDetailResponse,
    dependencies=[Depends(admin_ou_enfermagem)],
)
def desvincular_aluno(responsavel_id: int, aluno_id: int, db: Session = Depends(get_db)):
    responsavel = (
        db.query(Responsavel)
        .options(joinedload(Responsavel.alunos))
        .filter(Responsavel.id == responsavel_id)
        .first()
    )
    if not responsavel:
        raise HTTPException(status_code=404, detail="Responsável não encontrado")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    if aluno in responsavel.alunos:
        responsavel.alunos.remove(aluno)
        db.commit()
        db.refresh(responsavel)

    return responsavel

