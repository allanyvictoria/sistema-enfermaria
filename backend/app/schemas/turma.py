from pydantic import BaseModel
from typing import Literal  # 👈 Adicione este import

class TurmaCreate(BaseModel):
    nome: str
    sala_id: int
    # Limita o campo aceitar APENAS estas opções exatas:
    turno: Literal["MANHA", "TARDE", "NOITE", "INTEGRAL"] 
    ano_letivo: int


class TurmaResponse(BaseModel):
    id: int
    nome: str
    sala_id: int
    turno: str
    ano_letivo: int
    ativa: bool

    class Config:
        from_attributes = True