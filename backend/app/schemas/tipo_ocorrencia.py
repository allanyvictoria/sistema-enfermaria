from pydantic import BaseModel


class TipoOcorrenciaCreate(BaseModel):
    nome: str


class TipoOcorrenciaResponse(TipoOcorrenciaCreate):
    id: int
    ativo: bool

    class Config:
        from_attributes = True