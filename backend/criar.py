from app.database import SessionLocal
from app.models.usuario import Usuario
from app.auth.security import gerar_hash_senha


db = SessionLocal()

login = "admin"
senha = "admin123"

try:
    usuario = db.query(Usuario).filter(Usuario.login == login).first()

    if usuario:
        usuario.nome = "administrador"
        usuario.senha_hash = gerar_hash_senha(senha)
        usuario.tipo_acesso = "ADMIN"
        usuario.ativo = True
        db.commit()
        print("Profissional de Enfermagem já existia; dados atualizados!")
    else:
        usuario = Usuario(
            nome="administrador",
            login=login,
            senha_hash=gerar_hash_senha(senha),
            tipo_acesso="ADMIN",
            ativo=True
        )
        db.add(usuario)
        db.commit()
        print("administrador criado!")

    print("Login:", login)
    print("Senha:", senha)
except Exception as e:
    db.rollback()
    print(f"Erro ao criar administrador: {e}")
finally:
    db.close()