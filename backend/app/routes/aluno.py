from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.dependencies.auth import (
    admin_ou_enfermagem,
    get_usuario_atual,
    get_escola_id_atual,
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
    escola_id: int = Depends(get_escola_id_atual),
):
    return (
        db.query(Aluno)
        .options(joinedload(Aluno.matriculas).joinedload(Matricula.turma))
        .filter(Aluno.escola_id == escola_id)
        .all()
    )


@router.get("/{aluno_id}", response_model=AlunoResponse)
def buscar_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    aluno = (
        db.query(Aluno)
        .options(joinedload(Aluno.matriculas).joinedload(Matricula.turma))
        .filter(Aluno.id == aluno_id, Aluno.escola_id == escola_id)
        .first()
    )

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
    escola_id: int = Depends(get_escola_id_atual),
):
    # escola_id nunca vem do frontend — sempre da escola do usuário logado.
    aluno = Aluno(**dados.model_dump(), escola_id=escola_id)

    db.add(aluno)
    db.commit()
    db.refresh(aluno)

    return aluno


@router.put("/{aluno_id}", response_model=AlunoResponse)
def atualizar_aluno(
    aluno_id: int,
    dados: AlunoCreate, # ou um schema que aceite turma_id opcional
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    aluno = (
        db.query(Aluno)
        .options(joinedload(Aluno.matriculas).joinedload(Matricula.turma))
        .filter(Aluno.id == aluno_id, Aluno.escola_id == escola_id)
        .first()
    )

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )

    # Atualiza os dados cadastrais básicos (exceto se houver campos extras como turma_id soltos se o schema for AlunoCreate puro)
    dados_dict = dados.model_dump(exclude_unset=True)
    
    # Se o schema AlunoCreate não tiver turma_id, atualizamos os campos normais:
    for key, value in dados_dict.items():
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
    escola_id: int = Depends(get_escola_id_atual),
):
    aluno = (
        db.query(Aluno)
        .filter(Aluno.id == aluno_id, Aluno.escola_id == escola_id)
        .first()
    )

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
    escola_id: int = Depends(get_escola_id_atual),
):
    aluno = (
        db.query(Aluno)
        .options(
            joinedload(Aluno.ocorrencias),
            joinedload(Aluno.responsaveis),
        )
        .filter(Aluno.id == aluno_id, Aluno.escola_id == escola_id)
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
