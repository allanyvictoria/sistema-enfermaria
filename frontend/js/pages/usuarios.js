// =========================================================
// Pagina de Usuarios do sistema.
// Acesso restrito a ADMIN (o router e o menu ja escondem essa
// pagina de quem nao for admin; o backend tambem bloqueia via
// dependencia "somente_admin", entao a protecao vale nos dois lados)
// =========================================================

const TIPOS_ACESSO_USUARIO = [
  { valor: "ADMIN", label: "Administração" },
  { valor: "ENFERMAGEM", label: "Enfermagem" },
  { valor: "PROFESSORA", label: "Professor(a)" }
];

function labelTipoAcessoUsuario(tipo) {
  return TIPOS_ACESSO_USUARIO.find(t => t.valor === tipo)?.label || tipo;
}

async function renderUsuarios() {
  const content = renderAppShell({
    titulo: "Usuários do sistema",
    subtitulo: "Quem pode entrar no sistema e com qual nível de acesso.",
    acoesHtml: `<button class="btn btn-primary" id="btn-novo-usuario">${Icon.plus}<span>Novo usuário</span></button>`
  });

  content.innerHTML = `<div id="usuarios-lista">${loaderHtml("Carregando usuários...")}</div>`;

  document.getElementById("btn-novo-usuario").addEventListener("click", () => abrirFormUsuario());

  await carregarListaUsuarios();
}

async function carregarListaUsuarios() {
  const wrap = document.getElementById("usuarios-lista");
  let lista;
  try {
    lista = await Api.usuarios.listar();
  } catch (err) {
    if (wrap && !document.body.contains(wrap)) return;
    wrap.innerHTML = emptyStateHtml("Não foi possível carregar", err.message);
    return;
  }

  if (wrap && !document.body.contains(wrap)) return;

  if (!lista.length) {
    wrap.innerHTML = emptyStateHtml(
      "Nenhum usuário cadastrado",
      'Use o botão "Novo usuário" acima para criar o primeiro acesso.'
    );
    return;
  }

  const usuarioLogado = AuthStore.getUsuario();

  wrap.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Nome</th>
          <th>Login</th>
          <th>Perfil</th>
          <th>Status</th>
          <th></th>
        </tr></thead>
        <tbody>
          ${lista.map(u => `
            <tr>
              <td>${escapeHtml(u.nome)}</td>
              <td>${escapeHtml(u.login)}</td>
              <td><span class="pill pill-mint">${labelTipoAcessoUsuario(u.tipo_acesso)}</span></td>
              <td><span class="badge ${u.ativo ? "badge-ativo" : "badge-inativo"}">${u.ativo ? "Ativo" : "Inativo"}</span></td>
              <td>
                <div class="row-actions">
                  <button class="btn btn-soft btn-sm btn-icon editar-usuario" data-id="${u.id}" title="Editar">${Icon.edit}</button>
                  ${u.ativo && u.id !== usuarioLogado?.id
                    ? `<button class="btn btn-danger btn-sm btn-icon desativar-usuario" data-id="${u.id}" title="Desativar">${Icon.trash}</button>`
                    : ""}
                </div>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;

  wrap.querySelectorAll(".editar-usuario").forEach(btn => {
    btn.addEventListener("click", () => {
      const usuario = lista.find(u => u.id === Number(btn.dataset.id));
      abrirFormUsuario(usuario);
    });
  });

  wrap.querySelectorAll(".desativar-usuario").forEach(btn => {
    btn.addEventListener("click", () => {
      confirmarAcao({
        titulo: "Desativar usuário",
        mensagem: "Tem certeza que deseja desativar o acesso deste usuário? Ele não conseguirá mais fazer login até ser reativado.",
        corLabel: "Desativar",
        onConfirm: async () => {
          try {
            await Api.usuarios.desativar(Number(btn.dataset.id));
            showToast("Usuário desativado.", "success");
            carregarListaUsuarios();
          } catch (err) {
            showToast(err.message, "error");
          }
        }
      });
    });
  });
}

async function abrirFormUsuario(usuario = null) {
  const editando = !!usuario;

  abrirModal({
    titulo: editando ? "Editar usuário" : "Novo usuário",
    corpoHtml: `
      <form id="form-usuario">
        <div class="field">
          <label for="u-nome">Nome completo</label>
          <input type="text" id="u-nome" required value="${usuario ? escapeHtml(usuario.nome) : ""}" />
        </div>
        <div class="field">
          <label for="u-login">Login</label>
          <input type="text" id="u-login" required ${editando ? "readonly" : ""}
            value="${usuario ? escapeHtml(usuario.login) : ""}" placeholder="Ex.: joana.silva" />
          ${editando ? '<p class="small-muted" style="margin-top:4px;">O login não pode ser alterado depois de criado.</p>' : ""}
        </div>
        <div class="field">
          <label for="u-tipo">Perfil de acesso</label>
          <select id="u-tipo" required>
            ${TIPOS_ACESSO_USUARIO.map(t => `
              <option value="${t.valor}" ${usuario?.tipo_acesso === t.valor ? "selected" : ""}>${t.label}</option>
            `).join("")}
          </select>
        </div>
        <div class="field">
          <label for="u-senha">${editando ? "Nova senha (deixe em branco para manter a atual)" : "Senha"}</label>
          <input type="password" id="u-senha" ${editando ? "" : "required"} minlength="4"
            placeholder="${editando ? "••••••••" : "Mínimo 4 caracteres"}" />
        </div>
        ${editando ? `
          <div class="checkbox-field">
            <input type="checkbox" id="u-ativo" ${usuario.ativo ? "checked" : ""} />
            <label for="u-ativo" style="margin:0;">Usuário ativo (pode fazer login)</label>
          </div>
        ` : ""}
        <div class="modal-actions">
          <button type="button" class="btn btn-soft" id="cancelar-usuario">Cancelar</button>
          <button type="submit" class="btn btn-primary" id="salvar-usuario">${editando ? "Salvar alterações" : "Criar usuário"}</button>
        </div>
      </form>
    `,
    onMount: (overlay) => {
      overlay.querySelector("#cancelar-usuario").addEventListener("click", fecharModal);

      overlay.querySelector("#form-usuario").addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = overlay.querySelector("#salvar-usuario");
        btn.disabled = true;

        const nome = overlay.querySelector("#u-nome").value.trim();
        const login = overlay.querySelector("#u-login").value.trim();
        const tipo_acesso = overlay.querySelector("#u-tipo").value;
        const senha = overlay.querySelector("#u-senha").value;

        try {
          if (editando) {
            const ativo = overlay.querySelector("#u-ativo").checked;
            const dados = { nome, tipo_acesso, ativo };
            if (senha) dados.senha = senha;
            await Api.usuarios.atualizar(usuario.id, dados);
          } else {
            await Api.usuarios.criar({ nome, login, tipo_acesso, senha });
          }

          showToast("Usuário salvo com sucesso.", "success");
          fecharModal();
          carregarListaUsuarios();
        } catch (err) {
          showToast(err.message, "error");
        } finally {
          btn.disabled = false;
        }
      });
    }
  });
}
