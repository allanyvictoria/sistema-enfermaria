from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies.auth import get_escola_id_atual
from app.models.turma import Turma
from app.models.sala import Sala
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
def listar_turmas(
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    # Turma não tem escola_id direto — isolamento vem da sala.
    return (
        db.query(Turma)
        .join(Sala, Turma.sala_id == Sala.id)
        .filter(Sala.escola_id == escola_id)
        .all()
    )


@router.post("/", response_model=TurmaResponse, status_code=201)
def criar_turma(
    dados: TurmaCreate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    # Garante que a sala informada pertence à escola do usuário logado —
    # senão seria possível criar turma "vazando" pra sala de outra escola.
    sala = (
        db.query(Sala)
        .filter(Sala.id == dados.sala_id, Sala.escola_id == escola_id)
        .first()
    )
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

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
