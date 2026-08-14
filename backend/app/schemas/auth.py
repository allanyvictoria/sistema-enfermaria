from pydantic import BaseModel


class LoginRequest(BaseModel):
    login: str
    senha: str
    escola_id: int  # 👈 ADICIONADO — a tela de seleção de escola manda isso


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario_id: int
    tipo_acesso: str
    escola_id: int  # 👈 ADICIONADO — útil pro frontend exibir/guardar
