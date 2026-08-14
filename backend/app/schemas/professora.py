from pydantic import BaseModel
from app.schemas.turma import TurmaResponse


class ProfessoraCreate(BaseModel):
    nome: str
    telefone: str | None = None
    email: str | None = None


class ProfessoraResponse(ProfessoraCreate):
    id: int
    ativa: bool
    escola_id: int  # 👈 ADICIONADO
    turmas: list[TurmaResponse] = []

    class Config:
        from_attributes = True
