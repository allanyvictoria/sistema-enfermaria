from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno
from app.models.professora import Professora
from app.models.profissional_enfermagem import ProfissionalEnfermagem
from app.models.tipo_ocorrencia import TipoOcorrencia
from app.models.usuario import Usuario
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaResponse
from app.dependencies.auth import (
    get_usuario_atual,
    get_escola_id_atual,
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
    usuario: Usuario = Depends(get_usuario_atual),
    escola_id: int = Depends(get_escola_id_atual),
):
    # Confere que aluno, professora, profissional e tipo de ocorrência
    # pertencem TODOS à escola do usuário logado — evita registrar uma
    # ocorrência cruzando dados de escolas diferentes.
    aluno = db.query(Aluno).filter(
        Aluno.id == dados.aluno_id, Aluno.escola_id == escola_id
    ).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    professora = db.query(Professora).filter(
        Professora.id == dados.professora_id, Professora.escola_id == escola_id
    ).first()
    if not professora:
        raise HTTPException(status_code=404, detail="Professora não encontrada")

    profissional = db.query(ProfissionalEnfermagem).filter(
        ProfissionalEnfermagem.id == dados.profissional_id,
        ProfissionalEnfermagem.escola_id == escola_id,
    ).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    tipo = db.query(TipoOcorrencia).filter(
        TipoOcorrencia.id == dados.tipo_ocorrencia_id,
        TipoOcorrencia.escola_id == escola_id,
    ).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ocorrência não encontrado")

    ocorrencia = Ocorrencia(
        **dados.model_dump(),
        usuario_registrou_id=usuario.id  # 🚀 Agora pega o ID do usuário logado via JWT!
    )

    db.add(ocorrencia)
    db.commit()
    db.refresh(ocorrencia)

    # Busca a ocorrência criada recarregando os relacionamentos para o Schema
    return buscar_ocorrencia(ocorrencia.id, db, escola_id)


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
    escola_id: int = Depends(get_escola_id_atual),
):
    # Ocorrencia não tem escola_id direto — isolamento vem do aluno.
    consulta = (
        db.query(Ocorrencia)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .options(
            joinedload(Ocorrencia.aluno),
            joinedload(Ocorrencia.professora),
            joinedload(Ocorrencia.profissional),
            joinedload(Ocorrencia.tipo_ocorrencia)
        )
        .filter(Aluno.escola_id == escola_id)
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
    escola_id: int = Depends(get_escola_id_atual),
):
    ocorrencia = (
        db.query(Ocorrencia)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .options(
            joinedload(Ocorrencia.aluno),
            joinedload(Ocorrencia.professora),
            joinedload(Ocorrencia.profissional),
            joinedload(Ocorrencia.tipo_ocorrencia)
        )
        .filter(Ocorrencia.id == ocorrencia_id, Aluno.escola_id == escola_id)
        .first()
    )

    if not ocorrencia:
        raise HTTPException(
            status_code=404,
            detail="Ocorrência não encontrada"
        )

    return ocorrencia
