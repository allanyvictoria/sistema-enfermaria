// =========================================================
// Pagina de Relatorios em PDF
// =========================================================

async function renderRelatorios() {
  const content = renderAppShell({
    titulo: "Relatórios",
    subtitulo: "Gere documentos em PDF para acompanhamento e prontuário."
  });

  let alunos = [];
  try {
    alunos = await Api.alunos.listar();
  } catch {}

  // 👈 ADICIONADO: se o usuário já navegou pra outra página enquanto
  // esperava a API responder, "content" ficou órfão (fora do documento
  // atual). Continuar preenchendo e criando listeners nele quebraria
  // com "Cannot read properties of null (reading 'addEventListener')".
  if (!document.body.contains(content)) return;

  const hoje = new Date();

  content.innerHTML = `
    <div class="report-grid">
      <div class="report-card">
        <div class="r-icon">${Icon.calendar}</div>
        <h4>Relatório diário</h4>
        <p>Todos os atendimentos de um dia específico.</p>
        <div class="field">
          <label for="r-diario-data">Data</label>
          <input type="date" id="r-diario-data" value="${hoje_isoDate()}" />
        </div>
        <button class="btn btn-primary" style="width:100%;" id="btn-r-diario">${Icon.download}<span>Baixar PDF</span></button>
      </div>

      <div class="report-card">
        <div class="r-icon">${Icon.reportChart}</div>
        <h4>Relatório semanal</h4>
        <p>Resumo dos últimos 7 dias a partir da data escolhida.</p>
        <div class="field">
          <label for="r-semanal-data">Início da semana</label>
          <input type="date" id="r-semanal-data" />
        </div>
        <button class="btn btn-primary" style="width:100%;" id="btn-r-semanal">${Icon.download}<span>Baixar PDF</span></button>
      </div>

      <div class="report-card">
        <div class="r-icon">${Icon.folderHeart}</div>
        <h4>Relatório mensal</h4>
        <p>Consolidado de atendimentos do mês selecionado.</p>
        <div class="field-row">
          <div class="field">
            <label for="r-mensal-mes">Mês</label>
            <select id="r-mensal-mes">
              ${["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
                .map((m, i) => `<option value="${i + 1}" ${i + 1 === hoje.getMonth() + 1 ? "selected" : ""}>${m}</option>`).join("")}
            </select>
          </div>
          <div class="field">
            <label for="r-mensal-ano">Ano</label>
            <input type="number" id="r-mensal-ano" value="${hoje.getFullYear()}" min="2000" max="2100" />
          </div>
        </div>
        <button class="btn btn-primary" style="width:100%;" id="btn-r-mensal">${Icon.download}<span>Baixar PDF</span></button>
      </div>

      <div class="report-card">
        <div class="r-icon">${Icon.kids}</div>
        <h4>Prontuário do aluno</h4>
        <p>Histórico completo de saúde de um aluno específico.</p>
        <div class="field">
          <label for="r-aluno-id">Aluno</label>
          <select id="r-aluno-id"><option value="">Selecione...</option>${alunos.map(a => `<option value="${a.id}">${escapeHtml(a.nome)}</option>`).join("")}</select>
        </div>
        <button class="btn btn-primary" style="width:100%;" id="btn-r-aluno">${Icon.download}<span>Baixar PDF</span></button>
      </div>
    </div>
  `;

  async function baixarComFeedback(botaoId, chamada, nomeArquivo) {
    const btn = document.getElementById(botaoId);
    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "Gerando PDF...";
    try {
      const blob = await chamada();
      baixarBlob(blob, nomeArquivo);
      showToast("Relatório gerado com sucesso.", "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = textoOriginal;
    }
  }

  document.getElementById("btn-r-diario").addEventListener("click", () => {
    const data = document.getElementById("r-diario-data").value;
    baixarComFeedback("btn-r-diario", () => Api.relatorios.diario(data), `relatorio_diario_${data}.pdf`);
  });

  document.getElementById("btn-r-semanal").addEventListener("click", () => {
    const data = document.getElementById("r-semanal-data").value;
    baixarComFeedback("btn-r-semanal", () => Api.relatorios.semanal(data || undefined), `relatorio_semanal.pdf`);
  });

  document.getElementById("btn-r-mensal").addEventListener("click", () => {
    const mes = document.getElementById("r-mensal-mes").value;
    const ano = document.getElementById("r-mensal-ano").value;
    baixarComFeedback("btn-r-mensal", () => Api.relatorios.mensal(mes, ano), `relatorio_mensal_${mes}_${ano}.pdf`);
  });

  document.getElementById("btn-r-aluno").addEventListener("click", () => {
    const id = document.getElementById("r-aluno-id").value;
    if (!id) { showToast("Selecione um aluno primeiro.", "error"); return; }
    baixarComFeedback("btn-r-aluno", () => Api.relatorios.aluno(id), `historico_aluno_${id}.pdf`);
  });
}
