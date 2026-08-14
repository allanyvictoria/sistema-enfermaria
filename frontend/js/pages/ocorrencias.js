// =========================================================
// Pagina de Atendimentos (Ocorrencias)
// =========================================================

const RESULTADOS_PADRAO = [
  "Liberado para a sala",
  "Liberado para casa",
  "Aguardando responsável",
  "Encaminhado ao hospital",
  "Em observação na enfermaria",
  "Outro"
];

function pillResultado(resultado) {
  const mapa = {
    "Liberado para a sala": "pill-mint",
    "Liberado para casa": "pill-blue",
    "Aguardando responsável": "pill-sun",
    "Encaminhado ao hospital": "pill-rose",
    "Em observação na enfermaria": "pill-coral"
  };
  return `<span class="pill ${mapa[resultado] || "pill-blue"}">${escapeHtml(resultado || "-")}</span>`;
}

async function renderOcorrencias() {
  const podeCriar = AuthStore.temPerfil("ADMIN", "ENFERMAGEM");

  const content = renderAppShell({
    titulo: "Atendimentos",
    subtitulo: "Registros de idas à enfermaria.",
    acoesHtml: podeCriar
      ? `<button class="btn btn-primary" id="btn-novo-atendimento">${Icon.plus}<span>Novo atendimento</span></button>`
      : ""
  });

  content.innerHTML = `
    <div class="filters-bar card">
      <div class="field">
        <label for="f-aluno">Aluno</label>
        <select id="f-aluno"><option value="">Todos</option></select>
      </div>
      <div class="field">
        <label for="f-inicio">De</label>
        <input type="date" id="f-inicio" />
      </div>
      <div class="field">
        <label for="f-fim">Até</label>
        <input type="date" id="f-fim" />
      </div>
      <button class="btn btn-soft" id="btn-filtrar">${Icon.filter}<span>Filtrar</span></button>
      <button class="btn btn-outline" id="btn-limpar-filtro">Limpar</button>
    </div>
    <div id="ocorrencias-lista" style="margin-top:16px;">${loaderHtml("Carregando atendimentos...")}</div>
  `;

  let alunos = [];
  try {
    alunos = await Api.alunos.listar();
  } catch {}

  if (!document.body.contains(content)) return;

  const selAluno = document.getElementById("f-aluno");
  alunos.forEach(a => {
    const opt = document.createElement("option");
    opt.value = a.id;
    opt.textContent = a.nome;
    selAluno.appendChild(opt);
  });

  const listaWrap = document.getElementById("ocorrencias-lista");

  async function carregar(filtros = {}) {
    listaWrap.innerHTML = loaderHtml("Carregando atendimentos...");
    try {
      const lista = await Api.ocorrencias.listar(filtros);
      desenharLista(lista);
    } catch (err) {
      listaWrap.innerHTML = emptyStateHtml("Não foi possível carregar", err.message);
    }
  }

  function desenharLista(lista) {
    if (!lista.length) {
      listaWrap.innerHTML = emptyStateHtml("Nenhum atendimento por aqui", "Assim que um atendimento for registrado, ele aparecerá nesta lista.");
      return;
    }
    listaWrap.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>Data / hora</th><th>Aluno</th><th>Tipo</th><th>Profissional</th><th>Resultado</th>
          </tr></thead>
          <tbody>
            ${lista.map(o => `
              <tr class="clickable" data-id="${o.id}">
                <td>${formatarDataHora(o.data_hora)}</td>
                <td>${escapeHtml(o.aluno?.nome || "-")}</td>
                <td><span class="pill pill-blue">${escapeHtml(o.tipo_ocorrencia?.nome || "-")}</span></td>
                <td>${escapeHtml(o.profissional?.nome || "-")}</td>
                <td>${pillResultado(o.resultado)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
    listaWrap.querySelectorAll("tr.clickable").forEach(tr => {
      tr.addEventListener("click", () => abrirDetalheOcorrencia(Number(tr.dataset.id)));
    });
  }

  await carregar();

const btnFiltrar = document.getElementById("btn-filtrar");
if (btnFiltrar) {
  btnFiltrar.addEventListener("click", () => {
    carregar({
      aluno_id: selAluno?.value || undefined,
      data_inicio: document.getElementById("f-inicio")?.value || undefined,
      data_fim: document.getElementById("f-fim")?.value || undefined
    });
  });
}

  document.getElementById("btn-limpar-filtro").addEventListener("click", () => {
    selAluno.value = "";
    document.getElementById("f-inicio").value = "";
    document.getElementById("f-fim").value = "";
    carregar();
  });

  if (podeCriar) {
    document.getElementById("btn-novo-atendimento").addEventListener("click", () => abrirFormOcorrencia(alunos, carregar));
  }

  async function abrirDetalheOcorrencia(id) {
    abrirModal({
      titulo: "Detalhes do atendimento",
      corpoHtml: loaderHtml("Carregando..."),
      onMount: async (overlay) => {
        let o;
        try {
          o = await Api.ocorrencias.buscar(id);
        } catch (err) {
          overlay.querySelector(".modal-body").innerHTML = emptyStateHtml("Erro", err.message);
          return;
        }
        overlay.querySelector(".modal-body").innerHTML = `
          <div class="field-row">
            <div class="field"><label>Aluno</label><p style="color:var(--ink);font-weight:700;">${escapeHtml(o.aluno.nome)}</p></div>
            <div class="field"><label>Data / hora</label><p style="color:var(--ink);font-weight:700;">${formatarDataHora(o.data_hora)}</p></div>
          </div>
          <div class="field-row">
            <div class="field"><label>Tipo de ocorrência</label><p>${escapeHtml(o.tipo_ocorrencia.nome)}</p></div>
            <div class="field"><label>Turma</label><p>${escapeHtml(o.aluno?.turma?.nome || "-")}</p></div>            
          </div>
          <div class="field-row">
            <div class="field"><label>Professor(a)</label><p>${escapeHtml(o.professora.nome)}</p></div>
            <div class="field"><label>Profissional</label><p>${escapeHtml(o.profissional.nome)} <span class="small-muted">(${escapeHtml(o.profissional.funcao)})</span></p></div>
          </div>
          <div class="field-row">
          <div class="field"><label>Descrição</label><p>${escapeHtml(o.descricao)}</p></div>
          <div class="field"><label>Resultado</label><p>${pillResultado(o.resultado)}</p></div>
          </div class="field-row">
          <div class="field"><label>Conduta</label><p>${escapeHtml(o.conduta)}</p></div>
          ${o.observacoes ? `<div class="field"><label>Observações</label><p>${escapeHtml(o.observacoes)}</p></div>` : ""}
        `;
      }
    });
  }
}

async function abrirFormOcorrencia(alunosPrecarregados, aoSalvar) {
  let professoras = [], profissionais = [], tipos = [], responsaveis = [];
  try {
    [professoras, profissionais, tipos, responsaveis] = await Promise.all([
      Api.professoras.listar(),
      Api.profissionais.listar(),
      Api.tiposOcorrencia.listar(),
      Api.responsaveis.listar()
    ]);
  } catch (err) {
    showToast("Não foi possível carregar os dados do formulário: " + err.message, "error");
    return;
  }

  const opt = (lista, campoLabel = "nome") => lista.map(i => `<option value="${i.id}">${escapeHtml(i[campoLabel])}</option>`).join("");

  abrirModal({
    titulo: "Novo atendimento",
    wide: true,
    corpoHtml: `
      <form id="form-ocorrencia">
        <div class="field-row">
          <div class="field">
            <label for="o-aluno">Aluno</label>
            <select id="o-aluno" required><option value="">Selecione...</option>${opt(alunosPrecarregados)}</select>
          </div>
          <div class="field">
            <label for="o-tipo">Tipo de ocorrência</label>
            <select id="o-tipo" required><option value="">Selecione...</option>${opt(tipos)}</select>
          </div>
        </div>

        <div id="alerta-saude-aluno" style="margin-bottom: 12px;"></div>

        <div class="field-row">
          <div class="field">
            <label for="o-professora">Professora que acompanhou</label>
            <select id="o-professora" required><option value="">Selecione...</option>${opt(professoras)}</select>
          </div>
          <div class="field">
            <label for="o-profissional">Profissional de enfermagem</label>
            <select id="o-profissional" required><option value="">Selecione...</option>${opt(profissionais)}</select>
          </div>
        </div>
        <div class="field">
          <label for="o-descricao">Descrição do ocorrido</label>
          <textarea id="o-descricao" required placeholder="O que aconteceu?"></textarea>
        </div>
        <div class="field">
          <label for="o-conduta">Conduta tomada</label>
          <textarea id="o-conduta" required placeholder="Ex.: higienização do local, aplicação de gelo, aferição de temperatura..."></textarea>
        </div>
        <div class="field-row">
          <div class="field">
            <label for="o-resultado">Resultado</label>
            <select id="o-resultado" required>${RESULTADOS_PADRAO.map(r => `<option value="${escapeHtml(r)}">${escapeHtml(r)}</option>`).join("")}</select>
          </div>
          <div class="field">
            <label for="o-responsavel">Responsável que buscou (opcional)</label>
            <select id="o-responsavel"><option value="">Nenhum</option>${opt(responsaveis)}</select>
          </div>
        </div>
        <div class="field" id="campo-resultado-outro" style="display:none;">
          <label for="o-resultado-outro">Descreva o resultado</label>
          <input type="text" id="o-resultado-outro" maxlength="40" placeholder="Até 40 caracteres" />
        </div>
        <div class="field">
          <label for="o-obs">Observações adicionais (opcional)</label>
          <textarea id="o-obs" placeholder="Alguma informação extra..."></textarea>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-soft" id="cancelar-ocorrencia">Cancelar</button>
          <button type="submit" class="btn btn-primary" id="salvar-ocorrencia">Registrar atendimento</button>
        </div>
      </form>
    `,
    onMount: (overlay) => {
      const selAluno = overlay.querySelector("#o-aluno");
      const boxAlerta = overlay.querySelector("#alerta-saude-aluno");

      // Escutador para alertar sobre alergias/condições instantaneamente ao escolher o aluno
      selAluno.addEventListener("change", (e) => {
        const idAluno = Number(e.target.value);
        const aluno = alunosPrecarregados.find(a => a.id === idAluno);

        if (aluno && (aluno.alergias || aluno.condicoes_saude)) {
          boxAlerta.innerHTML = `
          <div style="background:#fef9c3; border-left:4px solid #eab308; padding:10px 14px; border-radius:8px; margin-top:4px;">
            <strong style="color:#854d0e; display:block; font-size:12px; font-weight:700;">🚨 ALERTA SOBRE CRIANÇA:</strong>
            ${aluno.alergias ? `<p style="margin:2px 0 0; color:#713f12; font-size:13px;"><strong>Alergias:</strong> ${escapeHtml(aluno.alergias)}</p>` : ""}
            ${aluno.condicoes_saude ? `<p style="margin:2px 0 0; color:#713f12; font-size:13px;"><strong>Condições:</strong> ${escapeHtml(aluno.condicoes_saude)}</p>` : ""}
          </div>
          `;
        } else {
          boxAlerta.innerHTML = "";
        }
      });

      const selResultado = overlay.querySelector("#o-resultado");
      const campoOutro = overlay.querySelector("#campo-resultado-outro");
      selResultado.addEventListener("change", () => {
        campoOutro.style.display = selResultado.value === "Outro" ? "block" : "none";
      });

      overlay.querySelector("#cancelar-ocorrencia").addEventListener("click", fecharModal);
      overlay.querySelector("#form-ocorrencia").addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = overlay.querySelector("#salvar-ocorrencia");
        btn.disabled = true;

        let resultado = selResultado.value;
        if (resultado === "Outro") {
          resultado = overlay.querySelector("#o-resultado-outro").value.trim();
        }

        const dados = {
          aluno_id: Number(overlay.querySelector("#o-aluno").value),
          professora_id: Number(overlay.querySelector("#o-professora").value),
          profissional_id: Number(overlay.querySelector("#o-profissional").value),
          tipo_ocorrencia_id: Number(overlay.querySelector("#o-tipo").value),
          descricao: overlay.querySelector("#o-descricao").value.trim(),
          conduta: overlay.querySelector("#o-conduta").value.trim(),
          resultado: resultado,
          responsavel_buscou_id: overlay.querySelector("#o-responsavel").value ? Number(overlay.querySelector("#o-responsavel").value) : null,
          observacoes: overlay.querySelector("#o-obs").value.trim() || null
        };

        try {
          await Api.ocorrencias.criar(dados);
          showToast("Atendimento registrado com sucesso.", "success");
          fecharModal();
          if (aoSalvar) aoSalvar();
        } catch (err) {
          showToast(err.message, "error");
        } finally {
          btn.disabled = false;
        }
      });
    }
  });
}