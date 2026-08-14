from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.schemas.turma import TurmaResponse

class OcorrenciaCreate(BaseModel):
    aluno_id: int
    professora_id: int
    profissional_id: int
    tipo_ocorrencia_id: int

    descricao: str
    conduta: str
    resultado: str

    responsavel_buscou_id: int | None = None
    observacoes: str | None = None
    observacao_posterior: str | None = None


class AlunoResumo(BaseModel):
    id: int
    nome: str
    turma: Optional[TurmaResponse] = None

    class Config:
        from_attributes = True


class ProfessoraResumo(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class ProfissionalResumo(BaseModel):
    id: int
    nome: str
    funcao: str

    class Config:
        from_attributes = True


class TipoOcorrenciaResumo(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class OcorrenciaResponse(BaseModel):
    id: int
    data_hora: datetime
    criado_em: datetime

    aluno: AlunoResumo
    professora: ProfessoraResumo
    profissional: ProfissionalResumo
    tipo_ocorrencia: TipoOcorrenciaResumo

    descricao: str
    conduta: str
    resultado: str

    responsavel_buscou_id: int | None
    observacoes: str | None
    observacao_posterior: str | None
    modificado_em: datetime | None

    class Config:
        from_attributes = True