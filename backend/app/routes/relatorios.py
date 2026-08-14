import io
from datetime import date, datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, extract
from sqlalchemy.orm import Session, joinedload
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.database import SessionLocal
from app.dependencies.auth import qualquer_usuario, get_escola_id_atual
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno
from app.models.tipo_ocorrencia import TipoOcorrencia

router = APIRouter(
    prefix="/relatorios",
    tags=["Relatórios"],
    dependencies=[Depends(qualquer_usuario)]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obter_estilos():
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'TituloPDF',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )
    subtitulo_style = ParagraphStyle(
        'SubtituloPDF',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )
    secao_style = ParagraphStyle(
        'SecaoPDF',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6
    )
    texto_celula = ParagraphStyle(
        'TextoCelula',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )
    return styles, titulo_style, subtitulo_style, secao_style, texto_celula


# ==========================================
# 1. RELATÓRIO DIÁRIO
# ==========================================
@router.get("/diario")
def relatorio_diario(
    data: date | None = None,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    data_consulta = data or date.today()
    inicio_dia = datetime.combine(data_consulta, time.min)
    fim_dia = datetime.combine(data_consulta, time.max)

    ocorrencias = (
        db.query(Ocorrencia)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .options(
            joinedload(Ocorrencia.aluno),
            joinedload(Ocorrencia.tipo_ocorrencia),
            joinedload(Ocorrencia.profissional)
        )
        .filter(
            Aluno.escola_id == escola_id,
            Ocorrencia.data_hora >= inicio_dia,
            Ocorrencia.data_hora <= fim_dia,
        )
        .order_by(Ocorrencia.data_hora.asc())
        .all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles, titulo_style, subtitulo_style, _, texto_celula = obter_estilos()

    elementos = [
        Paragraph("<b>Relatório Diário de Atendimentos</b>", titulo_style),
        Paragraph(f"Data: <b>{data_consulta.strftime('%d/%m/%Y')}</b> | Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitulo_style),
        Spacer(1, 10)
    ]

    if not ocorrencias:
        elementos.append(Paragraph("<i>Nenhum atendimento registrado nesta data.</i>", styles['Normal']))
    else:
        dados_tabela = [["Hora", "Aluno", "Tipo", "Profissional", "Conduta"]]
        for oc in ocorrencias:
            dados_tabela.append([
                Paragraph(f"<b>{oc.data_hora.strftime('%H:%M')}</b>", texto_celula),
                Paragraph(oc.aluno.nome if oc.aluno else "-", texto_celula),
                Paragraph(oc.tipo_ocorrencia.nome if oc.tipo_ocorrencia else "-", texto_celula),
                Paragraph(oc.profissional.nome if oc.profissional else "-", texto_celula),
                Paragraph(oc.conduta or "-", texto_celula)
            ])

        tabela = Table(dados_tabela, colWidths=[45, 120, 100, 110, 145])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabela)

    doc.build(elementos)
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=relatorio_diario_{data_consulta.strftime('%Y%m%d')}.pdf"}
    )


# ==========================================
# 2. RELATÓRIO SEMANAL
# ==========================================
@router.get("/semanal")
def relatorio_semanal(
    data_inicio: date | None = None,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    inicio = data_inicio or (date.today() - timedelta(days=6))
    fim = inicio + timedelta(days=6)
    dt_inicio = datetime.combine(inicio, time.min)
    dt_fim = datetime.combine(fim, time.max)

    base = (
        db.query(Ocorrencia)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            Ocorrencia.data_hora >= dt_inicio,
            Ocorrencia.data_hora <= dt_fim,
        )
    )

    total_atendimentos = base.with_entities(func.count(Ocorrencia.id)).scalar() or 0
    total_criancas = base.with_entities(func.count(func.distinct(Ocorrencia.aluno_id))).scalar() or 0

    por_tipo = (
        db.query(TipoOcorrencia.nome, func.count(Ocorrencia.id))
        .join(Ocorrencia, Ocorrencia.tipo_ocorrencia_id == TipoOcorrencia.id)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            Ocorrencia.data_hora >= dt_inicio,
            Ocorrencia.data_hora <= dt_fim,
        )
        .group_by(TipoOcorrencia.nome).all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles, titulo_style, subtitulo_style, secao_style, texto_celula = obter_estilos()

    elementos = [
        Paragraph("<b>Relatório Semanal de Atendimentos</b>", titulo_style),
        Paragraph(f"Período: <b>{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}</b>", subtitulo_style),
        Paragraph("<b>Indicadores Gerais</b>", secao_style),
        Paragraph(f"• Total de Atendimentos: <b>{total_atendimentos}</b><br/>• Crianças Atendidas: <b>{total_criancas}</b>", styles['Normal']),
        Spacer(1, 10),
        Paragraph("<b>Ocorrências por Tipo</b>", secao_style)
    ]

    tabela_tipo_dados = [["Tipo de Ocorrência", "Quantidade"]] + [[Paragraph(t, texto_celula), str(q)] for t, q in por_tipo]
    tabela_tipo = Table(tabela_tipo_dados, colWidths=[350, 170])
    tabela_tipo.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
    elementos.append(tabela_tipo)

    doc.build(elementos)
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=relatorio_semanal.pdf"})


# ==========================================
# 3. RELATÓRIO MENSAL
# ==========================================
@router.get("/mensal")
def relatorio_mensal(
    mes: int | None = None,
    ano: int | None = None,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    hoje = date.today()
    m = mes or hoje.month
    a = ano or hoje.year

    base = (
        db.query(Ocorrencia)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == m,
            extract('year', Ocorrencia.data_hora) == a,
        )
    )

    total_atendimentos = base.with_entities(func.count(Ocorrencia.id)).scalar() or 0
    total_criancas = base.with_entities(func.count(func.distinct(Ocorrencia.aluno_id))).scalar() or 0

    por_tipo = (
        db.query(TipoOcorrencia.nome, func.count(Ocorrencia.id))
        .join(Ocorrencia, Ocorrencia.tipo_ocorrencia_id == TipoOcorrencia.id)
        .join(Aluno, Ocorrencia.aluno_id == Aluno.id)
        .filter(
            Aluno.escola_id == escola_id,
            extract('month', Ocorrencia.data_hora) == m,
            extract('year', Ocorrencia.data_hora) == a,
        )
        .group_by(TipoOcorrencia.nome).order_by(func.count(Ocorrencia.id).desc()).all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles, titulo_style, subtitulo_style, secao_style, texto_celula = obter_estilos()

    elementos = [
        Paragraph("<b>Relatório Mensal de Enfermagem</b>", titulo_style),
        Paragraph(f"Mês/Ano: <b>{m:02d}/{a}</b> | Emitido em: {datetime.now().strftime('%d/%m/%Y')}", subtitulo_style),
        Paragraph("<b>Consolidado do Mês</b>", secao_style),
        Paragraph(f"• Total de Atendimentos Registrados: <b>{total_atendimentos}</b><br/>• Total de Alunos Distintos Atendidos: <b>{total_criancas}</b>", styles['Normal']),
        Spacer(1, 10),
        Paragraph("<b>Rank de Ocorrências por Tipo</b>", secao_style)
    ]

    dados_tabela = [["Tipo de Ocorrência", "Total no Mês"]] + [[Paragraph(t, texto_celula), str(q)] for t, q in por_tipo]
    tabela = Table(dados_tabela, colWidths=[350, 170])
    tabela.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
    elementos.append(tabela)

    doc.build(elementos)
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=relatorio_mensal_{m}_{a}.pdf"})


# ==========================================
# 4. HISTÓRICO INDIVIDUAL (PDF DO ALUNO)
# ==========================================
@router.get("/aluno/{aluno_id}")
def relatorio_historico_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    escola_id: int = Depends(get_escola_id_atual),
):
    aluno = (
        db.query(Aluno)
        .options(
            joinedload(Aluno.ocorrencias).joinedload(Ocorrencia.tipo_ocorrencia),
            joinedload(Aluno.ocorrencias).joinedload(Ocorrencia.profissional),
            joinedload(Aluno.responsaveis),
        )
        .filter(Aluno.id == aluno_id, Aluno.escola_id == escola_id)
        .first()
    )

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles, titulo_style, subtitulo_style, secao_style, texto_celula = obter_estilos()

    elementos = [
        Paragraph("<b>Prontuário e Histórico de Saúde do Aluno</b>", titulo_style),
        Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitulo_style),
        Paragraph("<b>Dados do Estudante</b>", secao_style),
        Paragraph(
            f"• Nome: <b>{aluno.nome}</b><br/>"
            f"• Data de Nascimento: <b>{aluno.data_nascimento.strftime('%d/%m/%Y')}</b><br/>"
            f"• Turma: <b>{aluno.turma.nome if aluno.turma else 'Não informado'}</b><br/>"
            f"• Observações / Alergias: <b>{aluno.observacoes or 'Nenhuma informação registrada'}</b>",
            styles['Normal']
        ),
        Spacer(1, 10),
        Paragraph("<b>Responsáveis Vinculados</b>", secao_style)
    ]

    if not aluno.responsaveis:
        elementos.append(Paragraph("<i>Nenhum responsável vinculado a este aluno.</i>", styles['Normal']))
    else:
        dados_resp = [["Nome", "Parentesco", "Telefone", "Autorizado a buscar"]]
        for r in aluno.responsaveis:
            dados_resp.append([
                Paragraph(r.nome, texto_celula),
                Paragraph(r.parentesco, texto_celula),
                Paragraph(r.telefone_principal, texto_celula),
                Paragraph("Sim" if r.autorizado_buscar else "Não", texto_celula),
            ])
        tabela_resp = Table(dados_resp, colWidths=[150, 90, 120, 130])
        tabela_resp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabela_resp)

    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("<b>Histórico de Atendimentos na Enfermaria</b>", secao_style))

    if not aluno.ocorrencias:
        elementos.append(Paragraph("<i>Nenhuma ocorrência registrada para este aluno.</i>", styles['Normal']))
    else:
        dados_tabela = [["Data/Hora", "Tipo", "Profissional", "Descrição / Conduta"]]
        for oc in aluno.ocorrencias:
            dados_tabela.append([
                Paragraph(oc.data_hora.strftime("%d/%m/%Y %H:%M"), texto_celula),
                Paragraph(oc.tipo_ocorrencia.nome if oc.tipo_ocorrencia else "-", texto_celula),
                Paragraph(oc.profissional.nome if oc.profissional else "-", texto_celula),
                Paragraph(f"<b>Desc:</b> {oc.descricao}<br/><b>Conduta:</b> {oc.conduta or '-'}", texto_celula)
            ])

        tabela = Table(dados_tabela, colWidths=[90, 90, 100, 240])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabela)

    doc.build(elementos)
    buffer.seek(0)
    nome_sanitizado = aluno.nome.lower().replace(" ", "_")
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=historico_{nome_sanitizado}.pdf"}
    )
