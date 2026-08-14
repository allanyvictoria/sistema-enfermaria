// =========================================================
// Estrutura fixa da aplicacao logada: barra lateral + topo
// =========================================================

const NAV_ITEMS = [
  { rota: "dashboard", label: "Painel", icon: "heartPulse", perfis: ["ADMIN", "ENFERMAGEM", "PROFESSOR(A)"] },
  { rota: "ocorrencias", label: "Atendimentos", icon: "clipboardCross", perfis: ["ADMIN", "ENFERMAGEM", "PROFESSOR(A)"] },
  { rota: "alunos", label: "Alunos", icon: "kids", perfis: ["ADMIN", "ENFERMAGEM", "PROFESSOR(A)"] },
  {
    rota: "cadastros", label: "Cadastros", icon: "folderHeart", perfis: ["ADMIN", "ENFERMAGEM"],
    sub: [
      { rota: "cadastros/turmas", label: "Turmas" },
      { rota: "cadastros/professoras", label: "Professores" },
      { rota: "cadastros/profissionais", label: "Equipe de enfermagem" },
      { rota: "cadastros/responsaveis", label: "Responsáveis" },
      { rota: "cadastros/tipos", label: "Tipos de ocorrência" }
    ]
  },
  { rota: "relatorios", label: "Relatórios", icon: "reportChart", perfis: ["ADMIN", "ENFERMAGEM", "PROFESSOR(A)"] },
  { rota: "usuarios", label: "Usuários", icon: "idBadge", perfis: ["ADMIN"] }
];

function nomeRotaAtual() {
  return (location.hash || "#/dashboard").replace(/^#\//, "");
}

function renderSidebar() {
  const usuario = AuthStore.getUsuario();
  const rotaAtual = nomeRotaAtual();
  const rotaBase = rotaAtual.split("/")[0];

  const itensHtml = NAV_ITEMS.filter(item => item.perfis.includes(usuario?.tipo_acesso))
    .map(item => {
      const ativo = rotaBase === item.rota;
      if (item.sub) {
        const subHtml = item.sub.map(s => `
          <a href="#/${s.rota}" class="nav-item ${rotaAtual === s.rota ? "active" : ""}">${s.label}</a>
        `).join("");
        return `
          <div class="nav-group">
            <a href="#/${item.sub[0].rota}" class="nav-item ${ativo ? "active" : ""}">
              ${Icon[item.icon]}<span>${item.label}</span>
            </a>
            <div class="nav-sub">${subHtml}</div>
          </div>
        `;
      }
      return `<a href="#/${item.rota}" class="nav-item ${ativo ? "active" : ""}">${Icon[item.icon]}<span>${item.label}</span></a>`;
    }).join("");

  const nomeLabel = {
    ADMIN: "Administração",
    ENFERMAGEM: "Enfermagem",
    PROFESSORA: "Professor(a)",
  }[usuario?.tipo_acesso] || usuario?.tipo_acesso;

  return `
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-brand">
        <img src="assets/illustrations/mascot.svg" alt="Mascote da enfermaria" />
        <div>
          <div class="name">Enfermaria<br/>Escolar</div>
        </div>
      </div>
      <nav>${itensHtml}</nav>
      <div class="sidebar-footer">
        <div class="user-chip">
          <div class="user-avatar">${iniciais(usuario?.nome)}</div>
          <div class="user-meta">
            <div class="u-name">${escapeHtml(usuario?.nome || "")}</div>
            <span class="role-badge role-${usuario?.tipo_acesso}">${nomeLabel}</span>
          </div>
        </div>
        <button class="btn btn-soft logout-btn" id="btn-logout" type="button">${Icon.logout}<span>Sair</span></button>
      </div>
    </aside>
  `;
}

function renderAppShell({ titulo, subtitulo = "", acoesHtml = "" }) {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="app-shell">
      ${renderSidebar()}
      <div class="main">
        <div class="topbar">
          <button class="btn btn-soft btn-icon menu-toggle" id="btn-menu" type="button" aria-label="Abrir menu">${Icon.menu}</button>
          <div>
            <h1>${escapeHtml(titulo)}</h1>
            ${subtitulo ? `<p class="subtitle">${escapeHtml(subtitulo)}</p>` : ""}
          </div>
          <div class="topbar-actions">${acoesHtml}</div>
        </div>
        <div class="content" id="page-content"></div>
      </div>
    </div>
  `;

  document.getElementById("btn-logout").addEventListener("click", () => {
    AuthStore.clear();
    location.hash = "#/login";
  });

  const btnMenu = document.getElementById("btn-menu");
  const sidebar = document.getElementById("sidebar");
  if (btnMenu) {
    btnMenu.addEventListener("click", () => sidebar.classList.toggle("open"));
  }

  // Fecha o menu lateral automaticamente ao clicar em qualquer link no celular
  document.querySelectorAll(".sidebar .nav-item").forEach(link => {
    link.addEventListener("click", () => {
      if (sidebar.classList.contains("open")) {
        sidebar.classList.remove("open");
      }
    });
  });

  return document.getElementById("page-content");
}
