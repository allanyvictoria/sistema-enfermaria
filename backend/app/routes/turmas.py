from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.turma import Turma
from app.schemas.turma import TurmaCreate, TurmaResponse


router = APIRouter(
    prefix="/turmas",
    tags=["Turmas"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[TurmaResponse])
def listar_turmas(db: Session = Depends(get_db)):
    return db.query(Turma).all()


@router.post("/", response_model=TurmaResponse, status_code=201)
def criar_turma(dados: TurmaCreate, db: Session = Depends(get_db)):
    turma = Turma(
        nome=dados.nome,
        sala_id=dados.sala_id,
        turno=dados.turno,
        ano_letivo=dados.ano_letivo
    )

    db.add(turma)
    db.commit()
    db.refresh(turma)

    return turma
