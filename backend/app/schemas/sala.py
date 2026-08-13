from pydantic import BaseModel


class SalaCreate(BaseModel):
    nome: str
    descricao: str | None = None


class SalaResponse(SalaCreate):
    id: int
    ativa: bool

    class Config:
        from_attributes = True