from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.dependencies.auth import (
    admin_ou_enfermagem,
    get_usuario_atual,
    somente_admin,
    qualquer_usuario,
)
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.usuario import Usuario
from app.schemas.aluno import ( 
    AlunoCreate, 
    AlunoResponse, 
    AlunoHistoricoResponse
)


router = APIRouter(
    prefix="/alunos",
    tags=["Alunos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[AlunoResponse],
    dependencies=[Depends(qualquer_usuario)]
)
def listar_alunos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"Usuário autenticado: {usuario.id} - {usuario.nome} ({usuario.tipo_acesso})")
    return db.query(Aluno).options(joinedload(Aluno.matriculas).joinedload(Matricula.turma)).all()


@router.get("/{aluno_id}", response_model=AlunoResponse)
def buscar_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"Usuário autenticado: {usuario.id} - {usuario.nome} ({usuario.tipo_acesso})")

    aluno = db.query(Aluno).options(joinedload(Aluno.matriculas).joinedload(Matricula.turma)).filter(Aluno.id == aluno_id).first()

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )

    return aluno


@router.post(
    "/",
    response_model=AlunoResponse,
    status_code=201,
    dependencies=[Depends(admin_ou_enfermagem)]
)
def criar_aluno(
    dados: AlunoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"Usuário autenticado: {usuario.id} - {usuario.nome} ({usuario.tipo_acesso})")

    aluno = Aluno(**dados.model_dump())

    db.add(aluno)
    db.commit()
    db.refresh(aluno)

    return aluno


@router.put("/{aluno_id}", response_model=AlunoResponse)
def atualizar_aluno(
    aluno_id: int,
    dados: AlunoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"Usuário autenticado: {usuario.id} - {usuario.nome} ({usuario.tipo_acesso})")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )

    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(aluno, key, value)

    db.commit()
    db.refresh(aluno)

    return aluno


@router.delete(
    "/{aluno_id}",
    dependencies=[Depends(somente_admin)]
)
def desativar_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"Usuário autenticado: {usuario.id} - {usuario.nome} ({usuario.tipo_acesso})")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )

    aluno.ativo = False

    db.commit()

    return {
        "mensagem": "Aluno desativado com sucesso",
        "usuario_id": usuario.id,
        "usuario_nome": usuario.nome,
    }


@router.get(
    "/{aluno_id}/historico", 
    response_model=AlunoHistoricoResponse,
    dependencies=[Depends(qualquer_usuario)]
)
def historico_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    aluno = (
        db.query(Aluno)
        .options(
            joinedload(Aluno.ocorrencias),
            joinedload(Aluno.responsaveis),
        )
        .filter(Aluno.id == aluno_id)
        .first()
    )

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )

    return {
        "aluno": aluno,
        "historico": aluno.ocorrencias
    }