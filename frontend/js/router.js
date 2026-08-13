// =========================================================
// Roteador simples baseado em hash (#/rota)
// =========================================================

const ROTAS_PUBLICAS = ["login"];

async function handleRoute() {
  fecharModal();
  destruirCharts?.();

  let rota = (location.hash || "#/login").replace(/^#\//, "");
  if (!rota) rota = "login";

  const logado = AuthStore.isLogado();

  if (!logado && !ROTAS_PUBLICAS.includes(rota.split("/")[0])) {
    location.hash = "#/login";
    return;
  }
  if (logado && rota === "login") {
    location.hash = "#/dashboard";
    return;
  }

  const [base, sub] = rota.split("/");

  try {
    switch (base) {
      case "login":
        renderLogin();
        break;
      case "dashboard":
        await renderDashboard();
        break;
      case "alunos":
        await renderAlunos();
        break;
      case "ocorrencias":
        await renderOcorrencias();
        break;
      case "cadastros": {
        const tab = sub && CADASTRO_CONFIG[sub] ? sub : "salas";
        if (!AuthStore.temPerfil("ADMIN", "ENFERMAGEM")) {
          location.hash = "#/dashboard";
          return;
        }
        await renderCadastros(tab);
        break;
      }
      case "relatorios":
        await renderRelatorios();
        break;
      case "usuarios":
        if (!AuthStore.temPerfil("ADMIN")) {
          location.hash = "#/dashboard";
          return;
        }
        await renderUsuarios();
        break;
      default:
        location.hash = "#/dashboard";
    }
  } catch (err) {
    console.error(err);
    showToast(err.message || "Ocorreu um erro inesperado.", "error");
  }
}

window.addEventListener("hashchange", handleRoute);
window.addEventListener("DOMContentLoaded", handleRoute);
