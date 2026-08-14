import sys

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models.escola import Escola
from app.auth.security import gerar_hash_senha


db = SessionLocal()

login = "admin"
senha = "admin123"

try:
    escolas = db.query(Escola).order_by(Escola.id).all()

    if not escolas:
        print("Nenhuma escola cadastrada ainda. Rode a migração "
              "(banco/migracao_multi_escola.sql) antes de criar usuários.")
        sys.exit(1)

    # escola_id pode vir como argumento (python criar_admin.py 2),
    # senão pergunta interativamente, senão cai pra única escola existente.
    escola_id = None

    if len(sys.argv) > 1:
        escola_id = int(sys.argv[1])
    elif len(escolas) == 1:
        escola_id = escolas[0].id
        print(f"Usando a única escola cadastrada: "
              f"[{escola_id}] {escolas[0].nome}")
    else:
        print("Escolas cadastradas:")
        for e in escolas:
            print(f"  [{e.id}] {e.nome}")
        escola_id = int(input("Digite o id da escola: "))

    if not any(e.id == escola_id for e in escolas):
        print(f"Escola com id {escola_id} não encontrada.")
        sys.exit(1)

    usuario = (
        db.query(Usuario)
        .filter(Usuario.login == login, Usuario.escola_id == escola_id)
        .first()
    )

    if usuario:
        usuario.nome = "Administrador"
        usuario.senha_hash = gerar_hash_senha(senha)
        usuario.tipo_acesso = "ADMIN"
        usuario.ativo = True
        db.commit()
        print("Administrador já existia; dados atualizados!")
    else:
        usuario = Usuario(
            nome="Administrador",
            login=login,
            escola_id=escola_id,
            senha_hash=gerar_hash_senha(senha),
            tipo_acesso="ADMIN",
            ativo=True
        )
        db.add(usuario)
        db.commit()
        print("Administrador criado!")

    print("Escola:", escola_id)
    print("Login:", login)
    print("Senha:", senha)
except Exception as e:
    db.rollback()
    print(f"Erro ao criar administrador: {e}")
finally:
    db.close()