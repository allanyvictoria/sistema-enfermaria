from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import func, extract, case
from sqlalchemy.orm import Session

from app.models.professora import Professora
from app.database import SessionLocal
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.tipo_ocorrencia import TipoOcorrencia
from app.dependencies.auth import qualquer_usuario, get_usuario_atual, get_escola_id_atual
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(qualquer_usuario)]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/resumo")
def resumo_dashboard(
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # ----------------------------------------------------
    #  1. INDICADORES DO MÊS
    # ----------------------------------------------------
    # Ocorrencia não tem escola_id direto — isolamento vem do aluno,
    # então toda query abaixo faz join com Aluno e filtra por escola_id.

    # Total de atendimentos no mês
    atendimentos_mes = (
        db.query(func.count(Ocorrencia.id))
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == mes_atual,
            extract('year', Ocorrencia.data_hora) == ano_atual
        ).scalar() or 0
    )

    # Total de crianças únicas atendidas no mês
    criancas_atendidas = (
        db.query(func.count(func.distinct(Ocorrencia.aluno_id)))
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == mes_atual,
            extract('year', Ocorrencia.data_hora) == ano_atual
        ).scalar() or 0
    )

    # Total de turmas distintas envolvidas no mês.
    turmas_envolvidas = (
        db.query(func.count(func.distinct(Matricula.turma_id)))
        .select_from(Ocorrencia)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .join(
            Matricula,
            (Matricula.aluno_id == Aluno.id) & (Matricula.data_fim.is_(None))
        )
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == mes_atual,
            extract('year', Ocorrencia.data_hora) == ano_atual
        ).scalar() or 0
    )

    # ----------------------------------------------------
    # 2. GRÁFICOS
    # ----------------------------------------------------
    
    #  A. Ocorrências por Dia no Mês
    por_dia_query = (
        db.query(
            func.date(Ocorrencia.data_hora).label("data"),
            func.count(Ocorrencia.id).label("quantidade")
        )
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == mes_atual,
            extract('year', Ocorrencia.data_hora) == ano_atual
        )
        .group_by(func.date(Ocorrencia.data_hora))
        .order_by(func.date(Ocorrencia.data_hora))
        .all()
    )
    ocorrencias_por_dia = [{"data": str(item.data), "quantidade": item.quantidade} for item in por_dia_query]

    #  B. Ocorrências por Tipo (Queda, Dor, Ferimento, etc.)
    por_tipo_query = (
        db.query(
            TipoOcorrencia.nome.label("tipo"),
            func.count(Ocorrencia.id).label("quantidade")
        )
        .join(Ocorrencia, Ocorrencia.tipo_ocorrencia_id == TipoOcorrencia.id)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == mes_atual,
            extract('year', Ocorrencia.data_hora) == ano_atual
        )
        .group_by(TipoOcorrencia.nome)
        .order_by(func.count(Ocorrencia.id).desc())
        .all()
    )
    ocorrencias_por_tipo = [{"tipo": item.tipo, "quantidade": item.quantidade} for item in por_tipo_query]

   #  C. Ocorrências por Sala / Turma (Turma do Aluno + Professora)
    # Buscamos as ocorrências do mês, já restritas à escola
    ocorrencias_mes = (
        db.query(Ocorrencia)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == mes_atual,
            extract('year', Ocorrencia.data_hora) == ano_atual
        )
        .all()
    )

    # Agrupamos em Python para usar a @property aluno.turma sem erros de SQL
    contagem_salas = {}

    for oc in ocorrencias_mes:
        nome_prof = oc.professora.nome if oc.professora else "Não informada"
        
        # Pega a turma do aluno (através da property aluno.turma)
        nome_turma = "Sem Turma"
        if oc.aluno and getattr(oc.aluno, "turma", None):
            turma_obj = oc.aluno.turma
            # Se turma_obj for o model Turma, pega .nome, senão converte pra string
            nome_turma = getattr(turma_obj, "nome", str(turma_obj))

        chave = (nome_turma, nome_prof)
        contagem_salas[chave] = contagem_salas.get(chave, 0) + 1

    # Monta a lista ordenada da maior quantidade para a menor
    ocorrencias_por_sala = [
        {
            "sala": f"{turma} - Profª {prof}",
            "turma": turma,
            "professora": prof,
            "quantidade": qtd
        }
        for (turma, prof), qtd in sorted(contagem_salas.items(), key=lambda item: item[1], reverse=True)
    ]
    #  D. Ocorrências por Turno (Manhã < 12h | Tarde >= 12h)
    turno_expr = case(
        (extract('hour', Ocorrencia.data_hora) < 12, 'Manhã'),
        else_='Tarde'
    ).label("turno")

    por_turno_query = (
        db.query(
            turno_expr,
            func.count(Ocorrencia.id).label("quantidade")
        )
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == mes_atual,
            extract('year', Ocorrencia.data_hora) == ano_atual
        )
        .group_by(turno_expr)
        .all()
    )
    ocorrencias_por_turno = [{"turno": item.turno, "quantidade": item.quantidade} for item in por_turno_query]

    # ----------------------------------------------------
    # RETORNO CONSOLIDADO
    # ----------------------------------------------------
    return {
        "indicadores": {
            "atendimentos_mes": atendimentos_mes,
            "criancas_atendidas": criancas_atendidas,
            "turmas_envolvidas": turmas_envolvidas
        },
        "graficos": {
            "por_dia": ocorrencias_por_dia,
            "por_tipo": ocorrencias_por_tipo,
            "por_sala": ocorrencias_por_sala,
            "por_turno": ocorrencias_por_turno
        }
    }
