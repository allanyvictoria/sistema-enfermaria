from pydantic import BaseModel


class EscolaResponse(BaseModel):
    id: int
    nome: str
    ativa: bool

    class Config:
        from_attributes = True
