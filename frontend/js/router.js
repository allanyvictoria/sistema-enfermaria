// =========================================================
// Roteador simples baseado em hash (#/rota)
// =========================================================

const ROTAS_PUBLICAS = ["login", "selecionar-escola"];

async function handleRoute() {
  fecharModal();
  destruirCharts?.();

  let rota = (location.hash || "#/login").replace(/^#\//, "");
  if (!rota) rota = "login";

  const logado = AuthStore.isLogado();
  const [base, sub] = rota.split("/");

  // Sem escola escolhida ainda: só a tela de seleção é permitida.
  if (!EscolaStore.isSelecionada() && base !== "selecionar-escola") {
    location.hash = "#/selecionar-escola";
    return;
  }

  if (!logado && !ROTAS_PUBLICAS.includes(base)) {
    location.hash = "#/login";
    return;
  }
  if (logado && (rota === "login" || rota === "selecionar-escola")) {
    location.hash = "#/dashboard";
    return;
  }

  try {
    switch (base) {
      case "selecionar-escola":
        await renderSelecionarEscola();
        break;
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
