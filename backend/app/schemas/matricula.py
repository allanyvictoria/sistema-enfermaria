from pydantic import BaseModel
from datetime import date


class MatriculaCreate(BaseModel):
    aluno_id: int
    turma_id: int
    data_inicio: date
    data_fim: date | None = None


class MatriculaResponse(BaseModel):
    id: int
    aluno_id: int
    turma_id: int
    data_inicio: date
    data_fim: date | None

    class Config:
        from_attributes = True
