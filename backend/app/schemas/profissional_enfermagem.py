from pydantic import BaseModel


class ProfissionalEnfermagemCreate(BaseModel):
    nome: str
    funcao: str
    registro_coren: str | None = None
    telefone: str | None = None


class ProfissionalEnfermagemResponse(ProfissionalEnfermagemCreate):
    id: int
    ativa: bool

    class Config:
        from_attributes = True