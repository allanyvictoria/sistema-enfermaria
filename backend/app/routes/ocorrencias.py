from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models.ocorrencia import Ocorrencia
from app.models.usuario import Usuario
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaResponse
from app.dependencies.auth import (
    get_usuario_atual,
    admin_ou_enfermagem,
    qualquer_usuario,
)


router = APIRouter(
    prefix="/ocorrencias",
    tags=["Ocorrências"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=OcorrenciaResponse,
    status_code=201,
    dependencies=[Depends(admin_ou_enfermagem)]
)
def criar_ocorrencia(
    dados: OcorrenciaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    ocorrencia = Ocorrencia(
        **dados.model_dump(),
        usuario_registrou_id=usuario.id  
    )

    db.add(ocorrencia)
    db.commit()
    db.refresh(ocorrencia)

    # Busca a ocorrência criada recarregando os relacionamentos para o Schema
    return buscar_ocorrencia(ocorrencia.id, db, usuario)


@router.get(
    "/",
    response_model=list[OcorrenciaResponse],
    dependencies=[Depends(qualquer_usuario)]
)
def listar_ocorrencias(
    aluno_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    consulta = (
        db.query(Ocorrencia)
        .options(
            joinedload(Ocorrencia.aluno),
            joinedload(Ocorrencia.professora),
            joinedload(Ocorrencia.profissional),
            joinedload(Ocorrencia.tipo_ocorrencia)
        )
    )

    if aluno_id:
        consulta = consulta.filter(Ocorrencia.aluno_id == aluno_id)

    if data_inicio:
        consulta = consulta.filter(Ocorrencia.data_hora >= data_inicio)

    if data_fim:
        consulta = consulta.filter(Ocorrencia.data_hora < data_fim)

    return consulta.order_by(Ocorrencia.data_hora.desc()).all()


@router.get(
    "/{ocorrencia_id}",
    response_model=OcorrenciaResponse,
    dependencies=[Depends(qualquer_usuario)]
)
def buscar_ocorrencia(
    ocorrencia_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    ocorrencia = (
        db.query(Ocorrencia)
        .options(
            joinedload(Ocorrencia.aluno),
            joinedload(Ocorrencia.professora),
            joinedload(Ocorrencia.profissional),
            joinedload(Ocorrencia.tipo_ocorrencia)
        )
        .filter(Ocorrencia.id == ocorrencia_id)
        .first()
    )

    if not ocorrencia:
        raise HTTPException(
            status_code=404,
            detail="Ocorrência não encontrada"
        )

    return ocorrencia