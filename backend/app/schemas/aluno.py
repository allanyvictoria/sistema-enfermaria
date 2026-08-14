from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.turma import TurmaResponse


# 📌 Colocamos o ResponsavelResumoSchema no topo para poder ser usado no AlunoResponse
class ResponsavelResumoSchema(BaseModel):
    id: int
    nome: str
    parentesco: str
    telefone_principal: str  # 👈 Corrigido: era 'telefone', mas no banco é 'telefone_principal'
    autorizado_buscar: bool = True

    class Config:
        from_attributes = True


# Dados que chegam do Front-End ao criar/editar
class AlunoCreate(BaseModel):
    nome: str
    data_nascimento: date
    foto_url: str | None = None
    observacoes: str | None = None
    alergias: str | None = None
    condicoes_saude: str | None = None
    # escola_id NÃO entra aqui — preenchido pelo backend a partir do
    # token de quem está logado (Etapa 4).


# Dados que a API responde para o Front-End
class AlunoResponse(BaseModel):
    id: int
    nome: str
    data_nascimento: date
    foto_url: str | None = None
    observacoes: str | None = None
    alergias: str | None = None
    condicoes_saude: str | None = None
    ativo: bool
    criado_em: datetime
    escola_id: int  # 👈 ADICIONADO
    responsaveis: list[ResponsavelResumoSchema] = []
    turma: Optional[TurmaResponse] = None

    class Config:
        from_attributes = True


class OcorrenciaResumoSchema(BaseModel):
    id: int
    data_hora: datetime
    descricao: str
    conduta: str | None = None
    resultado: str | None = None

    class Config:
        from_attributes = True


class AlunoHistoricoResponse(BaseModel):
    aluno: AlunoResponse
    historico: list[OcorrenciaResumoSchema]


class AlunoDetailSchema(BaseModel):
    id: int
    nome: str
    responsaveis: List[ResponsavelResumoSchema] = []

    class Config:
        from_attributes = True
