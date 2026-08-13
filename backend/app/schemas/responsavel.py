from datetime import date
from pydantic import BaseModel


class ResponsavelCreate(BaseModel):
    nome: str
    parentesco: str
    telefone_principal: str
    telefone_secundario: str | None = None
    email: str | None = None
    autorizado_buscar: bool = True



class AlunoResumoSchema(BaseModel):
    id: int
    nome: str
    data_nascimento: date
    ativo: bool

    class Config:
        from_attributes = True


class ResponsavelResponse(ResponsavelCreate):
    id: int

    class Config:
        from_attributes = True


class ResponsavelDetailResponse(ResponsavelResponse):
    alunos: list[AlunoResumoSchema] = []

    class Config:
        from_attributes = True