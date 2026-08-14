from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies.auth import get_escola_id_atual
from app.models.sala import Sala
from app.schemas.sala import SalaCreate, SalaResponse


router = APIRouter(
    prefix="/salas",
    tags=["Salas"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[SalaResponse])
def listar_salas(
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    return db.query(Sala).filter(Sala.escola_id == escola_id).all()


@router.get("/{sala_id}", response_model=SalaResponse)
def buscar_sala(
    sala_id: int,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    sala = (
        db.query(Sala)
        .filter(Sala.id == sala_id, Sala.escola_id == escola_id)
        .first()
    )

    if not sala:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada"
        )

    return sala


@router.post("/", response_model=SalaResponse, status_code=201)
def criar_sala(
    dados: SalaCreate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    sala = Sala(
        nome=dados.nome,
        descricao=dados.descricao,
        escola_id=escola_id
    )

    db.add(sala)
    db.commit()
    db.refresh(sala)

    return sala


@router.put("/{sala_id}", response_model=SalaResponse)
def atualizar_sala(
    sala_id: int,
    dados: SalaCreate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    sala = (
        db.query(Sala)
        .filter(Sala.id == sala_id, Sala.escola_id == escola_id)
        .first()
    )

    if not sala:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada"
        )

    sala.nome = dados.nome
    sala.descricao = dados.descricao

    db.commit()
    db.refresh(sala)

    return sala


@router.delete("/{sala_id}")
def desativar_sala(
    sala_id: int,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    sala = (
        db.query(Sala)
        .filter(Sala.id == sala_id, Sala.escola_id == escola_id)
        .first()
    )

    if not sala:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada"
        )

    sala.ativa = False

    db.commit()

    return {
        "mensagem": "Sala desativada com sucesso"
    }
