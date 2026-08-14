from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import SessionLocal
from app.dependencies.auth import get_escola_id_atual
from app.models.matricula import Matricula
from app.models.aluno import Aluno
from app.models.turma import Turma
from app.models.sala import Sala
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
def criar_matricula(
    dados: MatriculaCreate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    aluno = (
        db.query(Aluno)
        .filter(Aluno.id == dados.aluno_id, Aluno.escola_id == escola_id)
        .first()
    )

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Turma não tem escola_id direto — checa via sala.
    turma = (
        db.query(Turma)
        .join(Sala, Turma.sala_id == Sala.id)
        .filter(Turma.id == dados.turma_id, Sala.escola_id == escola_id)
        .first()
    )

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    # 📌 Se já existe matrícula ativa, encerra ela automaticamente (atribui a data de hoje como fim)
    ativa = db.query(Matricula).filter(Matricula.aluno_id == dados.aluno_id, Matricula.data_fim == None).first()

    if ativa:
        ativa.data_fim = dados.data_inicio or date.today()
        db.commit()

    # Cria a nova matrícula na turma nova
    matricula = Matricula(
        aluno_id=dados.aluno_id,
        turma_id=dados.turma_id,
        data_inicio=dados.data_inicio or date.today(),
        data_fim=dados.data_fim
    )

    db.add(matricula)
    db.commit()
    db.refresh(matricula)

    return matricula