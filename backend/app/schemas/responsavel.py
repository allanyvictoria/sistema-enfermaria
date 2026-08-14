from datetime import date
from pydantic import BaseModel


class ResponsavelCreate(BaseModel):
    nome: str
    parentesco: str
    telefone_principal: str
    telefone_secundario: str | None = None
    email: str | None = None
    autorizado_buscar: bool = True
    # escola_id NÃO entra aqui — preenchido pelo backend a partir do
    # token de quem está logado (Etapa 4), nunca vindo do frontend.


# 📌 Versão resumida do aluno, usada dentro da ficha do responsável
# (evita import circular com app.schemas.aluno)
class AlunoResumoSchema(BaseModel):
    id: int
    nome: str
    data_nascimento: date
    ativo: bool

    class Config:
        from_attributes = True


class ResponsavelResponse(ResponsavelCreate):
    id: int
    escola_id: int  # 👈 ADICIONADO

    class Config:
        from_attributes = True


# 📌 Ficha completa do responsável, com as crianças vinculadas
class ResponsavelDetailResponse(ResponsavelResponse):
    alunos: list[AlunoResumoSchema] = []

    class Config:
        from_attributes = True
