from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import SessionLocal
from app.models.matricula import Matricula
from app.models.aluno import Aluno
from app.schemas.matricula import MatriculaCreate, MatriculaResponse


router = APIRouter(
    prefix="/matriculas",
    tags=["Matriculas"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=MatriculaResponse, status_code=201)
def criar_matricula(dados: MatriculaCreate, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(Aluno.id == dados.aluno_id).first()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Verifica se existe matrícula ativa para o aluno
    ativa = db.query(Matricula).filter(Matricula.aluno_id == dados.aluno_id, Matricula.data_fim == None).first()

    if ativa:
        raise HTTPException(status_code=400, detail="Já existe matrícula ativa para este aluno. Finalize-a antes.")

    matricula = Matricula(
        aluno_id=dados.aluno_id,
        turma_id=dados.turma_id,
        data_inicio=dados.data_inicio,
        data_fim=dados.data_fim
    )

    db.add(matricula)
    db.commit()
    db.refresh(matricula)

    return matricula
