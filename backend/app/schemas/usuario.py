from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nome: str
    login: str
    tipo_acesso: str  # ADMIN, ENFERMAGEM ou PROFESSORA
    senha: str = Field(min_length=4)
    # escola_id NÃO entra aqui — é preenchido pelo backend a partir
    # do token de quem está logado (Etapa 4), nunca vindo do frontend.


class UsuarioUpdate(BaseModel):
    nome: str
    tipo_acesso: str
    ativo: bool
    senha: str | None = Field(default=None, min_length=4)


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    login: str
    tipo_acesso: str
    ativo: bool
    escola_id: int  # 👈 ADICIONADO

    class Config:
        from_attributes = True
