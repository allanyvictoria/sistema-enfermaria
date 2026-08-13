from pydantic import BaseModel


class LoginRequest(BaseModel):
    login: str
    senha: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario_id: int
    tipo_acesso: str