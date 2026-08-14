// =========================================================
// Tela de seleção de escola — exibida antes do login.
// =========================================================

async function renderSelecionarEscola() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="login-screen">
      <div class="login-card">
        <div class="login-visual">
          <img src="assets/illustrations/login-hero.svg" alt="Ilustração de ursinho enfermeiro com maleta de primeiros socorros e coração" />
          <h2>Cuidando de cada sorriso</h2>
          <p>Um cantinho tranquilo para acompanhar a saúde das crianças na escola.</p>
        </div>
        <div class="login-form">
          <div class="brand">
            <img src="assets/illustrations/mascot.svg" alt="" />
            <span>ENFERMARIA ESCOLAR</span>
          </div>
          <h2>Qual é a sua escola?</h2>
          <p style="margin-bottom:22px;">Selecione a escola para continuar.</p>

          <div class="form-error" id="escola-error"></div>

          <div id="lista-escolas" style="display:flex;flex-direction:column;gap:10px;">
            <p style="color:var(--ink-faint);">Carregando escolas...</p>
          </div>
        </div>
      </div>
    </div>
  `;

  const lista = document.getElementById("lista-escolas");
  const erroBox = document.getElementById("escola-error");

  try {
    const escolas = await Api.escolas.listar();

    if (!escolas || escolas.length === 0) {
      lista.innerHTML = `<p style="color:var(--ink-faint);">Nenhuma escola cadastrada no momento. Fale com o suporte.</p>`;
      return;
    }

    lista.innerHTML = escolas
      .map(
        (e) => `
        <button
          type="button"
          class="btn btn-outline"
          style="width:100%;padding:14px;justify-content:flex-start;text-align:left;font-size:15px;"
          data-escola-id="${e.id}"
          data-escola-nome="${e.nome}"
        >
          ${e.nome}
        </button>
      `
      )
      .join("");

    lista.querySelectorAll("[data-escola-id]").forEach((btn) => {
      btn.addEventListener("click", () => {
        EscolaStore.set({
          id: Number(btn.dataset.escolaId),
          nome: btn.dataset.escolaNome
        });
        location.hash = "#/login";
      });
    });
  } catch (err) {
    erroBox.textContent = err.message || "Não foi possível carregar as escolas.";
    erroBox.classList.add("show");
    lista.innerHTML = "";
  }
}
