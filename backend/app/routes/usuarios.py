from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies.auth import somente_admin, get_usuario_atual, get_escola_id_atual
from app.models.usuario import Usuario
from app.auth.security import gerar_hash_senha
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse


# somente_admin fica no router inteiro: nenhuma rota abaixo funciona
# para quem não estiver logado como ADMIN.
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
    dependencies=[Depends(somente_admin)],
)

TIPOS_VALIDOS = {"ADMIN", "ENFERMAGEM", "PROFESSORA"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    return (
        db.query(Usuario)
        .filter(Usuario.escola_id == escola_id)
        .order_by(Usuario.nome)
        .all()
    )


@router.post("/", response_model=UsuarioResponse, status_code=201)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    if dados.tipo_acesso not in TIPOS_VALIDOS:
        raise HTTPException(400, "Tipo de acesso inválido")

    # Login único por escola (duas escolas podem ter cada uma seu "admin").
    existente = db.query(Usuario).filter(
        Usuario.login == dados.login, Usuario.escola_id == escola_id
    ).first()
    if existente:
        raise HTTPException(400, "Já existe um usuário com esse login nesta escola")

    usuario = Usuario(
        nome=dados.nome,
        login=dados.login,
        escola_id=escola_id,
        senha_hash=gerar_hash_senha(dados.senha),
        tipo_acesso=dados.tipo_acesso,
        ativo=True,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_usuario_atual),
    escola_id: int = Depends(get_escola_id_atual),
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id, Usuario.escola_id == escola_id
    ).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")

    if dados.tipo_acesso not in TIPOS_VALIDOS:
        raise HTTPException(400, "Tipo de acesso inválido")

    # Trava de segurança: um admin não pode se autodesativar nem
    # tirar o próprio acesso de administrador (evita ficar trancado fora).
    if usuario.id == usuario_logado.id and not dados.ativo:
        raise HTTPException(400, "Você não pode desativar o seu próprio usuário")

    if usuario.id == usuario_logado.id and dados.tipo_acesso != "ADMIN":
        raise HTTPException(400, "Você não pode remover seu próprio acesso de administrador")

    usuario.nome = dados.nome
    usuario.tipo_acesso = dados.tipo_acesso
    usuario.ativo = dados.ativo

    if dados.senha:
        usuario.senha_hash = gerar_hash_senha(dados.senha)

    db.commit()
    db.refresh(usuario)

    return usuario


@router.delete("/{usuario_id}")
def desativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_usuario_atual),
    escola_id: int = Depends(get_escola_id_atual),
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id, Usuario.escola_id == escola_id
    ).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")

    if usuario.id == usuario_logado.id:
        raise HTTPException(400, "Você não pode desativar o seu próprio usuário")

    usuario.ativo = False
    db.commit()

    return {"mensagem": "Usuário desativado com sucesso"}
