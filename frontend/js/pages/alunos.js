// =========================================================
// Pagina de Alunos: listagem, cadastro, historico
// =========================================================

let _alunosCache = [];

async function renderAlunos() {
  const usuario = AuthStore.getUsuario();
  const podeGerenciar = AuthStore.temPerfil("ADMIN", "ENFERMAGEM");
  const podeExcluir = AuthStore.temPerfil("ADMIN");

  const content = renderAppShell({
    titulo: "Alunos",
    subtitulo: "Fichas e histórico de saúde de cada criança.",
    acoesHtml: podeGerenciar
      ? `<button class="btn btn-primary" id="btn-novo-aluno">${Icon.plus}<span>Novo aluno</span></button>`
      : ""
  });

  content.innerHTML = `
    <div class="section-head">
      <div class="search-box">
        ${Icon.search}
        <input type="text" id="busca-aluno" placeholder="Buscar aluno pelo nome..." />
      </div>
    </div>
    <div id="alunos-grid">${loaderHtml("Buscando os alunos...")}</div>
  `;

  if (podeGerenciar) {
    document.getElementById("btn-novo-aluno").addEventListener("click", () => abrirFormAluno());
  }

  const grid = document.getElementById("alunos-grid");

  try {
    _alunosCache = await Api.alunos.listar();
  } catch (err) {
    if (!document.body.contains(content)) return;
    grid.innerHTML = emptyStateHtml("Não foi possível carregar os alunos", err.message);
    return;
  }

  if (!document.body.contains(content)) return; 

  const desenharGrid = (lista) => {
    if (!lista.length) {
      grid.innerHTML = emptyStateHtml("Nenhum aluno encontrado", "Cadastre o primeiro aluno para começar a acompanhar os atendimentos.");
      return;
    }
    grid.innerHTML = `<div class="aluno-grid">${lista.map(a => `
      <div class="aluno-card" data-id="${a.id}">
        <div class="aluno-photo">${a.foto_url ? `<img src="${escapeHtml(a.foto_url)}" alt="Foto de ${escapeHtml(a.nome)}" onerror="this.parentElement.innerHTML='${iniciais(a.nome)}'"/>` : iniciais(a.nome)}</div>
        <div class="a-name">${escapeHtml(a.nome)}</div>
        <div class="a-age">${calcularIdade(a.data_nascimento)}</div>
        <span class="badge ${a.ativo ? "badge-ativo" : "badge-inativo"}">${a.ativo ? "Ativo" : "Inativo"}</span>
        
        <div style="display:flex; flex-direction:column; gap:4px; margin-top:8px; width:100%; align-items:center;">
          ${a.alergias ? `<span class="pill pill-rose" style="font-size:11px; white-space:nowrap; text-overflow:ellipsis; overflow:hidden; max-width:100%;" title="Alergia: ${escapeHtml(a.alergias)}">⚠️ ${escapeHtml(a.alergias)}</span>` : ""}
          ${a.condicoes_saude ? `<span class="pill pill-sun" style="font-size:11px; white-space:nowrap; text-overflow:ellipsis; overflow:hidden; max-width:100%;" title="Condição: ${escapeHtml(a.condicoes_saude)}">🩺 ${escapeHtml(a.condicoes_saude)}</span>` : ""}
        </div>
      </div>
    `).join("")}</div>`;

    grid.querySelectorAll(".aluno-card").forEach(card => {
      card.addEventListener("click", () => abrirDetalheAluno(Number(card.dataset.id)));
    });
  };

  desenharGrid(_alunosCache);

  document.getElementById("busca-aluno").addEventListener("input", (e) => {
    const termo = e.target.value.trim().toLowerCase();
    desenharGrid(_alunosCache.filter(a => a.nome.toLowerCase().includes(termo)));
  });

  async function abrirDetalheAluno(id) {
    abrirModal({
      titulo: "Ficha do aluno",
      wide: true,
      corpoHtml: loaderHtml("Carregando ficha e histórico..."),
      onMount: async (overlay) => {
        let dados;
        try {
          dados = await Api.alunos.historico(id);
        } catch (err) {
          overlay.querySelector(".modal-body").innerHTML = emptyStateHtml("Erro ao carregar", err.message);
          return;
        }
        const aluno = dados.aluno;
        const historico = dados.historico || [];
        const responsaveis = aluno.responsaveis || [];

        overlay.querySelector(".modal-body").innerHTML = `
          <div style="display:flex;gap:16px;align-items:center;margin-bottom:18px;">
            <div class="aluno-photo" style="width:64px;height:64px;font-size:19px;">${iniciais(aluno.nome)}</div>
            <div>
              <h3 style="margin-bottom:2px;">${escapeHtml(aluno.nome)}</h3>
              <p class="small-muted">Ficha nº ${aluno.id}</p>
              <p class="small-muted">Nascimento: ${formatarData(aluno.data_nascimento)} (${calcularIdade(aluno.data_nascimento)})</p>
              <p class="small-muted">Turma: ${aluno.turma ? escapeHtml(aluno.turma.nome) : "-"}</p>
            </div>
          </div>

          ${(aluno.alergias || aluno.condicoes_saude) ? `
            <div style="background:#fef2f2; border-left:4px solid #ef4444; padding:12px 14px; border-radius:8px; margin-bottom:18px;">
              <strong style="color:#991b1b; display:block; margin-bottom:4px; font-size:13px;">⚠️ ALERTAS DE SAÚDE DA CRIANÇA</strong>
              ${aluno.alergias ? `<p style="margin:2px 0; color:#7f1d1d; font-size:13px;"><strong>Alergias:</strong> ${escapeHtml(aluno.alergias)}</p>` : ""}
              ${aluno.condicoes_saude ? `<p style="margin:2px 0; color:#7f1d1d; font-size:13px;"><strong>Condições de saúde:</strong> ${escapeHtml(aluno.condicoes_saude)}</p>` : ""}
            </div>
          ` : ""}

          <h4 style="font-size:14px;color:var(--ink-soft);margin-bottom:10px;">Responsáveis vinculados</h4>
          ${responsaveis.length === 0
            ? `<p class="small-muted" style="margin-bottom:18px;">Nenhum responsável vinculado. Vincule pela tela de Cadastros › Responsáveis.</p>`
            : `<div style="display:flex;flex-direction:column;gap:6px;margin-bottom:18px;">${responsaveis.map(r => `
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--surface-soft, #F8FAFC);border-radius:10px;">
                  <div>
                    <strong>${escapeHtml(r.nome)}</strong>
                    <span class="small-muted"> · ${escapeHtml(r.parentesco)}</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <span class="small-muted">${escapeHtml(r.telefone_principal)}</span>
                    <span class="pill ${r.autorizado_buscar ? "pill-mint" : "pill-rose"}">${r.autorizado_buscar ? "Pode buscar" : "Não autorizado"}</span>
                  </div>
                </div>
              `).join("")}</div>`
          }



          <h4 style="font-size:14px;color:var(--ink-soft);margin-bottom:10px;">Histórico de atendimentos</h4>
          ${historico.length === 0
            ? `<p class="small-muted">Nenhum atendimento registrado até o momento.</p>`
            : `<div class="timeline">${historico.map(h => `
                <div class="timeline-item">
                  <div class="t-date">${formatarDataHora(h.data_hora)}</div>
                  <div class="t-desc">${escapeHtml(h.descricao)}</div>
                  <div class="t-meta">${h.conduta ? "Conduta: " + escapeHtml(h.conduta) : ""} ${h.resultado ? " · Resultado: " + escapeHtml(h.resultado) : ""}</div>
                </div>
              `).join("")}</div>`
          }

          <div class="modal-actions" style="justify-content:space-between;">
            <button class="btn btn-outline btn-sm" id="btn-baixar-historico" type="button">${Icon.download}<span>Baixar PDF</span></button>
            <div style="display:flex;gap:8px;">
              ${podeGerenciar ? `<button class="btn btn-soft btn-sm" id="btn-editar-aluno" type="button">${Icon.edit}<span>Editar</span></button>` : ""}
              ${podeExcluir ? `<button class="btn btn-danger btn-sm" id="btn-desativar-aluno" type="button">${Icon.trash}<span>Desativar</span></button>` : ""}
            </div>
          </div>
        `;

        overlay.querySelector("#btn-baixar-historico").addEventListener("click", async (e) => {
          const btn = e.currentTarget;
          btn.disabled = true;
          try {
            const blob = await Api.relatorios.aluno(id);
            baixarBlob(blob, `historico_${aluno.nome.toLowerCase().replace(/\s+/g, "_")}.pdf`);
          } catch (err) {
            showToast(err.message, "error");
          } finally {
            btn.disabled = false;
          }
        });

        const btnEditar = overlay.querySelector("#btn-editar-aluno");
        if (btnEditar) btnEditar.addEventListener("click", async () => {
          const alunoCompleto = _alunosCache.find(a => a.id === id);
          fecharModal();
          abrirFormAluno(alunoCompleto);
        });

        const btnDesativar = overlay.querySelector("#btn-desativar-aluno");
        if (btnDesativar) btnDesativar.addEventListener("click", () => {
          confirmarAcao({
            titulo: "Desativar aluno",
            mensagem: `Tem certeza que deseja desativar ${aluno.nome}? Ele deixará de aparecer como ativo no sistema.`,
            corLabel: "Desativar",
            onConfirm: async () => {
              try {
                await Api.alunos.desativar(id);
                showToast("Aluno desativado com sucesso.", "success");
                renderAlunos();
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          });
        });
      }
    });
  }

  function abrirFormAluno(aluno = null) {
    const editando = !!aluno;
    abrirModal({
      titulo: editando ? "Editar aluno" : "Novo aluno",
      corpoHtml: `
        <form id="form-aluno">
          <div class="field">
            <label for="a-nome">Nome completo</label>
            <input type="text" id="a-nome" required value="${aluno ? escapeHtml(aluno.nome) : ""}" placeholder="Nome do aluno" />
          </div>
          <div class="field">
            <label for="a-nasc">Data de nascimento</label>
            <input type="date" id="a-nasc" required value="${aluno ? aluno.data_nascimento : ""}" />
          </div>
          <div class="field">
            <label for="a-alergias">Alergias (se houver)</label>
            <input type="text" id="a-alergias" value="${aluno?.alergias ? escapeHtml(aluno.alergias) : ""}" placeholder="Ex.: Dipirona, Amendoim, Abelha..." />
          </div>
          <div class="field">
            <label for="a-condicoes">Condições de saúde / DVs (se houver)</label>
            <input type="text" id="a-condicoes" value="${aluno?.condicoes_saude ? escapeHtml(aluno.condicoes_saude) : ""}" placeholder="Ex.: Asma, Diabetes Tipo 1, Intolerância a Lactose..." />
          </div>
          <div class="field">
            <label for="a-foto">Link da foto (opcional)</label>
            <input type="url" id="a-foto" value="${aluno?.foto_url ? escapeHtml(aluno.foto_url) : ""}" placeholder="https://..." />
          </div>
          <div class="field">
            <label for="a-turma">Turma</label>
            <select id="a-turma">
              <option value="">-- Nenhuma --</option>
            </select>
          </div>
          <div class="field">
            <label for="a-obs">Observações</label>
            <textarea id="a-obs" placeholder="Ex.: observações gerais">${aluno?.observacoes ? escapeHtml(aluno.observacoes) : ""}</textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-soft" id="cancelar-aluno">Cancelar</button>
            <button type="submit" class="btn btn-primary" id="salvar-aluno">${editando ? "Salvar alterações" : "Cadastrar aluno"}</button>
          </div>
        </form>
      `,
      onMount: (overlay) => {
        (async () => {
          let turmas = [];
          try {
            turmas = await Api.turmas.listar();
          } catch (err) {
            console.warn('Falha ao carregar turmas', err);
          }
          const sel = overlay.querySelector('#a-turma');
          turmas.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = `${t.nome} — ${t.turno} ${t.ano_letivo}`;
            sel.appendChild(opt);
          });
          if (aluno && aluno.turma && aluno.turma.id) sel.value = aluno.turma.id;
        })();

        overlay.querySelector("#cancelar-aluno").addEventListener("click", fecharModal);
        overlay.querySelector("#form-aluno").addEventListener("submit", async (e) => {
          e.preventDefault();
          const btn = overlay.querySelector("#salvar-aluno");
          btn.disabled = true;
          const dados = {
            nome: overlay.querySelector("#a-nome").value.trim(),
            data_nascimento: overlay.querySelector("#a-nasc").value,
            alergias: overlay.querySelector("#a-alergias").value.trim() || null,
            condicoes_saude: overlay.querySelector("#a-condicoes").value.trim() || null,
            foto_url: overlay.querySelector("#a-foto").value.trim() || null,
            observacoes: overlay.querySelector("#a-obs").value.trim() || null
          };
          try {
            if (editando) {
              await Api.alunos.atualizar(aluno.id, dados);
              showToast("Dados do aluno atualizados.", "success");
              const turmaSel = overlay.querySelector('#a-turma').value;
              if (turmaSel && (!aluno.turma || !aluno.turma.id)) {
                const hoje = new Date().toISOString().slice(0,10);
                await Api.matriculas.criar({ aluno_id: aluno.id, turma_id: Number(turmaSel), data_inicio: hoje });
              }
            } else {
              const criado = await Api.alunos.criar(dados);
              showToast("Aluno cadastrado com sucesso.", "success");
              const turmaSel = overlay.querySelector('#a-turma').value;
              if (turmaSel) {
                const hoje = new Date().toISOString().slice(0,10);
                await Api.matriculas.criar({ aluno_id: criado.id, turma_id: Number(turmaSel), data_inicio: hoje });
              }
            }
            fecharModal();
            renderAlunos();
          } catch (err) {
            showToast(err.message, "error");
          } finally {
            btn.disabled = false;
          }
        });
      }
    });
  }
}