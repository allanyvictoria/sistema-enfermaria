// =========================================================
// Pagina de Cadastros (Salas, Professoras, Profissionais,
// Responsaveis e Tipos de Ocorrencia) - aba unica reutilizavel
// =========================================================

const CADASTRO_CONFIG = {
  turmas: {
    titulo: "Turmas",
    singular: "Turma",
    subtitulo: "Turmas e turnos atendidos pela enfermaria.",
    get api() { return Api.turmas; },
    podeEditar: false,
    podeDesativar: false,
    campoAtivo: "ativa",
    colunas: [
      { label: "Nome da Turma", campo: "nome" },
      { label: "Turno", campo: "turno" },
      { label: "Ano Letivo", campo: "ano_letivo" }
    ],
    campos: [
      { id: "nome", label: "Nome da Turma", tipo: "text", required: true, placeholder: "Ex.: 1º Ano A" },
      { id: "turno", label: "Turno", tipo: "select", required: true, opcoes: ["MANHA", "TARDE", "NOITE", "INTEGRAL"] },
      { id: "ano_letivo", label: "Ano Letivo", tipo: "number", required: true, padrao: new Date().getFullYear() }
    ]
  },
  professoras: {
    titulo: "Professores",
    singular: "Professor(a)",
    subtitulo: "Equipe docente que acompanha os alunos.",
    get api() { return Api.professoras; },
    podeEditar: true,
    podeDesativar: true,
    gerenciaVinculos: true, 
    campoAtivo: "ativa",
    colunas: [
      { label: "Nome", campo: "nome" },
      { label: "Telefone", campo: "telefone", vazio: "-" },
      { label: "E-mail", campo: "email", vazio: "-" },
      { label: "Turmas vinculadas", campo: "turmas", tipo: "lista" }  
    ],
    campos: [
      { id: "nome", label: "Nome completo", tipo: "text", required: true },
      { id: "telefone", label: "Telefone (opcional)", tipo: "tel", placeholder: "(00) 00000-0000" },
      { id: "email", label: "E-mail (opcional)", tipo: "email" }
    ]
  },
  profissionais: {
    titulo: "Equipe de enfermagem",
    singular: "Profissional de enfermagem",
    subtitulo: "Profissionais responsáveis pelos atendimentos.",
    get api() { return Api.profissionais; },
    podeEditar: false,
    podeDesativar: false,
    campoAtivo: "ativa",
    colunas: [
      { label: "Nome", campo: "nome" },
      { label: "Função", campo: "funcao" },
      { label: "COREN", campo: "registro_coren", vazio: "-" },
      { label: "Telefone", campo: "telefone", vazio: "-" }
    ],
    campos: [
      { id: "nome", label: "Nome completo", tipo: "text", required: true },
      { id: "funcao", label: "Função", tipo: "select", required: true, opcoes: ["ENFERMEIRO(A)", "TECNICO(A)", "AUXILIAR"] },
      { id: "registro_coren", label: "Registro COREN (opcional)", tipo: "text" },
      { id: "telefone", label: "Telefone (opcional)", tipo: "tel", placeholder: "(00) 00000-0000" }
    ]
  },
  responsaveis: {
    titulo: "Responsáveis",
    singular: "Responsável",
    subtitulo: "Pessoas autorizadas a buscar os alunos.",
    get api() { return Api.responsaveis; },
    podeEditar: false,
    podeDesativar: false,
    gerenciaVinculos: true,
    colunas: [
      { label: "Nome", campo: "nome" },
      { label: "Parentesco", campo: "parentesco" },
      { label: "Telefone", campo: "telefone_principal" },
      { label: "Crianças vinculadas", campo: "alunos", tipo: "lista" },
      { label: "Autorizado a buscar", campo: "autorizado_buscar", tipo: "bool" }
    ],
    campos: [
      { id: "nome", label: "Nome completo", tipo: "text", required: true },
      { id: "parentesco", label: "Parentesco", tipo: "text", required: true, placeholder: "Ex.: Mãe, Pai, Avó..." },
      { id: "telefone_principal", label: "Telefone principal", tipo: "tel", required: true, placeholder: "(00) 00000-0000" },
      { id: "telefone_secundario", label: "Telefone secundário (opcional)", tipo: "tel" },
      { id: "email", label: "E-mail (opcional)", tipo: "email" },
      { id: "autorizado_buscar", label: "Autorizado(a) a buscar o aluno na escola", tipo: "checkbox", padrao: true }
    ]
  },
  tipos: {
    titulo: "Tipos de ocorrência",
    singular: "Tipo de ocorrência",
    subtitulo: "Categorias usadas ao registrar um atendimento.",
    get api() { return Api.tiposOcorrencia; },
    podeEditar: false,
    podeDesativar: false,
    campoAtivo: "ativo",
    colunas: [
      { label: "Nome", campo: "nome" }
    ],
    campos: [
      { id: "nome", label: "Nome do tipo de ocorrência", tipo: "text", required: true, placeholder: "Ex.: Febre, Queda, Corte..." }
    ]
  }
};

const CADASTRO_TABS = [
  { key: "turmas", label: "Turmas" },
  { key: "professoras", label: "Professores" },
  { key: "profissionais", label: "Equipe de enfermagem" },
  { key: "responsaveis", label: "Responsáveis" },
  { key: "tipos", label: "Tipos de ocorrência" }
];

async function renderCadastros(tabAtual) {
  const cfg = CADASTRO_CONFIG[tabAtual];
  const content = renderAppShell({
    titulo: "Cadastros",
    subtitulo: cfg.subtitulo,
    acoesHtml: `<button class="btn btn-primary" id="btn-novo-item">${Icon.plus}<span>Adicionar</span></button>`
  });

  content.innerHTML = `
    <div class="tabs">
      ${CADASTRO_TABS.map(t => `<button class="tab-btn ${t.key === tabAtual ? "active" : ""}" data-tab="${t.key}">${t.label}</button>`).join("")}
    </div>
    <div id="cadastro-lista">${loaderHtml("Carregando...")}</div>
  `;

  content.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => { location.hash = `#/cadastros/${btn.dataset.tab}`; });
  });

  document.getElementById("btn-novo-item").addEventListener("click", () => abrirFormCadastro(cfg));

  await carregarLista(cfg);
}

async function carregarLista(cfg) {
  const wrap = document.getElementById("cadastro-lista");
  let lista;
  try {
    lista = await cfg.api.listar();
  } catch (err) {
    if (wrap && !document.body.contains(wrap)) return;
    wrap.innerHTML = emptyStateHtml("Não foi possível carregar", err.message);
    return;
  }

  if (wrap && !document.body.contains(wrap)) return;

  if (!lista.length) {
    wrap.innerHTML = emptyStateHtml(`Nenhum registro em ${cfg.titulo.toLowerCase()}`, "Use o botão \"Adicionar\" acima para criar o primeiro registro.");
    return;
  }

  const mostrarAcoes = cfg.podeEditar || cfg.podeDesativar || cfg.gerenciaVinculos;

  wrap.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr>
          ${cfg.colunas.map(c => `<th>${c.label}</th>`).join("")}
          ${cfg.campoAtivo ? "<th>Status</th>" : ""}
          ${mostrarAcoes ? '<th></th>' : ""}
        </tr></thead>
        <tbody>
          ${lista.map(item => `
            <tr>
              ${cfg.colunas.map(c => {
                if (c.tipo === "bool") return `<td>${item[c.campo] ? `<span class="pill pill-mint">Sim</span>` : `<span class="pill pill-rose">Não</span>`}</td>`;
                if (c.tipo === "lista") {
                  const itens = item[c.campo] || [];
                  if (!itens.length) return `<td><span class="small-muted">Nenhuma vinculada</span></td>`;
                  return `<td>${itens.map(x => `<span class="pill pill-mint" style="margin:2px 4px 2px 0;display:inline-block;">${escapeHtml(x.nome)}</span>`).join("")}</td>`;
                }
                return `<td>${escapeHtml(item[c.campo] ?? c.vazio ?? "-")}</td>`;
              }).join("")}
              ${cfg.campoAtivo ? `<td><span class="badge ${item[cfg.campoAtivo] ? "badge-ativo" : "badge-inativo"}">${item[cfg.campoAtivo] ? "Ativo" : "Inativo"}</span></td>` : ""}
              ${mostrarAcoes ? `
                <td>
                  <div class="row-actions">
                    ${cfg.gerenciaVinculos ? `<button class="btn btn-soft btn-sm btn-icon gerenciar-vinculos" data-id="${item.id}" title="Gerenciar crianças vinculadas">${Icon.link}</button>` : ""}
                    ${cfg.podeEditar ? `<button class="btn btn-soft btn-sm btn-icon editar-item" data-id="${item.id}" title="Editar">${Icon.edit}</button>` : ""}
                    ${cfg.podeDesativar && item[cfg.campoAtivo] ? `<button class="btn btn-danger btn-sm btn-icon desativar-item" data-id="${item.id}" title="Desativar">${Icon.trash}</button>` : ""}
                  </div>
                </td>` : ""}
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;

  if (cfg.podeEditar) {
    wrap.querySelectorAll(".editar-item").forEach(btn => {
      btn.addEventListener("click", () => {
        const item = lista.find(i => i.id === Number(btn.dataset.id));
        abrirFormCadastro(cfg, item);
      });
    });
  }
  if (cfg.podeDesativar) {
    wrap.querySelectorAll(".desativar-item").forEach(btn => {
      btn.addEventListener("click", () => {
        confirmarAcao({
          titulo: "Desativar registro",
          mensagem: "Tem certeza que deseja desativar este registro?",
          corLabel: "Desativar",
          onConfirm: async () => {
            try {
              await cfg.api.desativar(Number(btn.dataset.id));
              showToast("Registro desativado.", "success");
              carregarLista(cfg);
            } catch (err) {
              showToast(err.message, "error");
            }
          }
        });
      });
    });
  }
  if (cfg.gerenciaVinculos) {
    wrap.querySelectorAll(".gerenciar-vinculos").forEach(btn => {
      btn.addEventListener("click", () => {
        const item = lista.find(i => i.id === Number(btn.dataset.id));
        abrirGerenciarVinculos(cfg, item);
      });
    });
  }
}

// =========================================================
// Vincular/desvincular crianças a um responsável
// =========================================================
async function abrirGerenciarVinculos(cfg, item) {
  const isProfessora = cfg === CADASTRO_CONFIG.professoras;

  const tituloModal = isProfessora 
    ? `Turmas vinculadas a ${item.nome}`
    : `Crianças vinculadas a ${item.nome}`;

  const textoAjuda = isProfessora
    ? "Marque as turmas em que esta professora leciona."
    : "Marque as crianças que este responsável acompanha. A ligação aparece na ficha da criança e nos relatórios.";

  abrirModal({
    titulo: tituloModal,
    corpoHtml: loaderHtml("Carregando opções..."),
    onMount: async (overlay) => {
      let listaOpcoes;
      try {
        listaOpcoes = isProfessora ? await Api.turmas.listar() : await Api.alunos.listar();
      } catch (err) {
        overlay.querySelector(".modal-body").innerHTML = emptyStateHtml("Erro ao carregar lista", err.message);
        return;
      }

      // Pega os IDs já vinculados (turmas ou alunos)
      const vinculadosIds = new Set(((isProfessora ? item.turmas : item.alunos) || []).map(x => x.id));

      const desenhar = () => {
        overlay.querySelector(".modal-body").innerHTML = `
          <p class="small-muted" style="margin-bottom:12px;">${textoAjuda}</p>
          <div class="checklist" style="max-height:340px;overflow-y:auto;">
            ${listaOpcoes.map(o => `
              <label class="checkbox-field" style="display:flex;align-items:center;gap:8px;padding:6px 0;">
                <input type="checkbox" class="chk-vinculo" data-opcao-id="${o.id}" ${vinculadosIds.has(o.id) ? "checked" : ""} />
                <span>${escapeHtml(o.nome)}</span>
              </label>
            `).join("")}
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-soft" id="fechar-vinculos">Fechar</button>
          </div>
        `;

        overlay.querySelector("#fechar-vinculos").addEventListener("click", () => {
          fecharModal();
          carregarLista(cfg);
        });

        overlay.querySelectorAll(".chk-vinculo").forEach(chk => {
          chk.addEventListener("change", async () => {
            const opcaoId = Number(chk.dataset.opcaoId);
            chk.disabled = true;
            try {
              if (chk.checked) {
                await cfg.api.vincular(item.id, opcaoId);
                vinculadosIds.add(opcaoId);
                showToast("Vínculo criado.", "success");
              } else {
                await cfg.api.desvincular(item.id, opcaoId);
                vinculadosIds.delete(opcaoId);
                showToast("Vínculo removido.", "success");
              }
            } catch (err) {
              chk.checked = !chk.checked;
              showToast(err.message, "error");
            } finally {
              chk.disabled = false;
            }
          });
        });
      };

      desenhar();
    }
  });
}

async function abrirFormCadastro(cfg, item = null) {
  const editando = !!item;
  const isProfessora = cfg === CADASTRO_CONFIG.professoras;

  // Busca a lista de turmas se for professora
  let turmasDisponiveis = [];
  if (isProfessora) {
    try {
      turmasDisponiveis = await Api.turmas.listar();
    } catch (err) {
      console.error("Erro ao carregar turmas:", err);
    }
  }

  // Normaliza os IDs das turmas atuais para Números (garante compatibilidade texto/número)
  const turmasAtuaisIds = new Set(
    (item?.turmas || []).map(t => Number(typeof t === "object" ? t.id : t))
  );

  // Renderiza os campos padrões do formulário
  const camposHtml = cfg.campos.map(c => {
    const valor = item ? item[c.id] : (c.padrao !== undefined ? c.padrao : "");
    if (c.tipo === "select") {
      return `
        <div class="field">
          <label for="c-${c.id}">${c.label}</label>
          <select id="c-${c.id}" ${c.required ? "required" : ""}>
            ${c.opcoes.map(o => `<option value="${o}" ${valor === o ? "selected" : ""}>${o}</option>`).join("")}
          </select>
        </div>`;
    }
    if (c.tipo === "checkbox") {
      return `
        <div class="checkbox-field">
          <input type="checkbox" id="c-${c.id}" ${valor ? "checked" : ""} />
          <label for="c-${c.id}" style="margin:0;">${c.label}</label>
        </div>`;
    }
    return `
      <div class="field">
        <label for="c-${c.id}">${c.label}</label>
        <input type="${c.tipo}" id="c-${c.id}" ${c.required ? "required" : ""} value="${valor ? escapeHtml(valor) : ""}" placeholder="${c.placeholder || ""}" />
      </div>`;
  }).join("");

  // Se for Professora, gera as checkboxes das turmas
  const htmlTurmas = isProfessora ? `
    <div class="field" style="margin-top:12px;">
      <label style="font-weight:600;margin-bottom:6px;display:block;">Turmas lecionadas (opcional):</label>
      <div class="checklist" style="max-height:160px;overflow-y:auto;border:1px solid var(--border,#e2e8f0);padding:8px;border-radius:8px;">
        ${turmasDisponiveis.length ? turmasDisponiveis.map(t => {
          const tId = Number(t.id);
          const marcado = turmasAtuaisIds.has(tId);
          return `
            <label class="checkbox-field" style="display:flex;align-items:center;gap:8px;padding:4px 0;cursor:pointer;">
              <input type="checkbox" class="form-chk-turma" value="${tId}" ${marcado ? "checked" : ""} />
              <span>${escapeHtml(t.nome)} ${t.turno ? `(${t.turno})` : ""}</span>
            </label>
          `;
        }).join("") : '<p class="small-muted">Nenhuma turma cadastrada ainda.</p>'}
      </div>
    </div>
  ` : "";

  abrirModal({
    titulo: editando ? `Editar ${cfg.singular.toLowerCase()}` : `Novo(a) ${cfg.singular.toLowerCase()}`,
    corpoHtml: `
      <form id="form-cadastro">
        ${camposHtml}
        ${htmlTurmas}
        <div class="modal-actions">
          <button type="button" class="btn btn-soft" id="cancelar-cadastro">Cancelar</button>
          <button type="submit" class="btn btn-primary" id="salvar-cadastro">${editando ? "Salvar alterações" : "Cadastrar"}</button>
        </div>
      </form>
    `,
    onMount: (overlay) => {
      overlay.querySelector("#cancelar-cadastro").addEventListener("click", fecharModal);
      overlay.querySelector("#form-cadastro").addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = overlay.querySelector("#salvar-cadastro");
        btn.disabled = true;

        const dados = {};
        cfg.campos.forEach(c => {
          const el = overlay.querySelector(`#c-${c.id}`);
          if (c.tipo === "checkbox") {
            dados[c.id] = el.checked;
          } else {
            const v = el.value.trim();
            dados[c.id] = v === "" ? null : v;
          }
        });

        try {
          let profId = item?.id;

          if (editando && cfg.podeEditar) {
            await cfg.api.atualizar(item.id, dados);
          } else {
            if (cfg === CADASTRO_CONFIG.turmas) {
              const novaSala = await Api.salas.criar({
                nome: dados.nome,
                descricao: `Sala da turma ${dados.nome}`
              });

              const payloadTurma = {
                nome: dados.nome,
                sala_id: novaSala.id,
                turno: dados.turno,
                ano_letivo: Number(dados.ano_letivo)
              };

              await Api.turmas.criar(payloadTurma);
            } else {
              const respostaCriacao = await cfg.api.criar(dados);
              if (isProfessora && respostaCriacao?.id) {
                profId = respostaCriacao.id;
              }
            }
          }

          // Se for Professora, sincroniza as turmas selecionadas
          if (isProfessora && profId) {
            const turmasSelecionadas = Array.from(overlay.querySelectorAll(".form-chk-turma:checked"))
              .map(chk => Number(chk.value));

            // 1. Turmas para vincular (novas marcações)
            const paraVincular = turmasSelecionadas.filter(id => !turmasAtuaisIds.has(id));
            for (const tId of paraVincular) {
              await Api.professoras.vincular(profId, tId);
            }

            // 2. Turmas para desvincular (desmarcadas na edição)
            if (editando) {
              const paraDesvincular = Array.from(turmasAtuaisIds).filter(id => !turmasSelecionadas.includes(id));
              for (const tId of paraDesvincular) {
                await Api.professoras.desvincular(profId, tId);
              }
            }
          }

          showToast("Registro salvo com sucesso.", "success");
          fecharModal();
          carregarLista(cfg);
        } catch (err) {
          showToast(err.message, "error");
        } finally {
          btn.disabled = false;
        }
      });
    }
  });
}