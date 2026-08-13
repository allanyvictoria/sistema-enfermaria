from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.professora import Professora
from app.models.turma import Turma  
from app.schemas.professora import ProfessoraCreate, ProfessoraResponse


router = APIRouter(
    prefix="/professoras",
    tags=["Professoras"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ProfessoraResponse])
def listar_professoras(db: Session = Depends(get_db)):
    return db.query(Professora).all()


@router.get("/{professora_id}", response_model=ProfessoraResponse)
def buscar_professora(
    professora_id: int,
    db: Session = Depends(get_db)
):
    professora = db.query(Professora).filter(
        Professora.id == professora_id
    ).first()

    if not professora:
        raise HTTPException(404, "Professora não encontrada")

    return professora


@router.post("/", response_model=ProfessoraResponse, status_code=201)
def criar_professora(
    dados: ProfessoraCreate,
    db: Session = Depends(get_db)
):
    professora = Professora(**dados.model_dump())

    db.add(professora)
    db.commit()
    db.refresh(professora)

    return professora


@router.put("/{professora_id}", response_model=ProfessoraResponse)
def atualizar_professora(
    professora_id: int,
    dados: ProfessoraCreate,
    db: Session = Depends(get_db)
):
    professora = db.query(Professora).filter(
        Professora.id == professora_id
    ).first()

    if not professora:
        raise HTTPException(404, "Professora não encontrada")

    for campo, valor in dados.model_dump().items():
        setattr(professora, campo, valor)

    db.commit()
    db.refresh(professora)

    return professora


@router.delete("/{professora_id}")
def desativar_professora(
    professora_id: int,
    db: Session = Depends(get_db)
):
    professora = db.query(Professora).filter(
        Professora.id == professora_id
    ).first()

    if not professora:
        raise HTTPException(404, "Professora não encontrada")

    professora.ativa = False

    db.commit()

    return {"mensagem": "Professora desativada com sucesso"}


@router.post("/{professora_id}/vincular/{turma_id}")
def vincular_turma(
    professora_id: int,
    turma_id: int,
    db: Session = Depends(get_db)
):
    professora = db.query(Professora).filter(Professora.id == professora_id).first()
    if not professora:
        raise HTTPException(404, "Professora não encontrada")

    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if not turma:
        raise HTTPException(404, "Turma não encontrada")

    if turma not in professora.turmas:
        professora.turmas.append(turma)
        db.commit()

    return {"mensagem": "Turma vinculada com sucesso"}


@router.delete("/{professora_id}/vincular/{turma_id}")
def desvincular_turma(
    professora_id: int,
    turma_id: int,
    db: Session = Depends(get_db)
):
    professora = db.query(Professora).filter(Professora.id == professora_id).first()
    if not professora:
        raise HTTPException(404, "Professora não encontrada")

    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if not turma:
        raise HTTPException(404, "Turma não encontrada")

    if turma in professora.turmas:
        professora.turmas.remove(turma)
        db.commit()

    return {"mensagem": "Turma desvinculada com sucesso"}