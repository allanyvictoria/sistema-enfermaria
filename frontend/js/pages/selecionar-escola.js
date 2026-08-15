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
          <p style="margin-bottom:16px;">Selecione a escola para continuar.</p>

          <div class="form-error" id="escola-error"></div>

          <div class="field" id="campo-busca-escola" style="display:none;margin-bottom:14px;">
            <input type="text" id="busca-escola" placeholder="Buscar escola pelo nome..." autocomplete="off" />
          </div>

          <div id="lista-escolas" class="escola-grid">
            <p style="color:var(--ink-faint);grid-column:1/-1;">Carregando escolas...</p>
          </div>
        </div>
      </div>
    </div>
  `;

  const lista = document.getElementById("lista-escolas");
  const erroBox = document.getElementById("escola-error");
  const campoBusca = document.getElementById("campo-busca-escola");
  const inputBusca = document.getElementById("busca-escola");

  function selecionar(escola) {
    EscolaStore.set({ id: escola.id, nome: escola.nome });
    location.hash = "#/login";
  }

  function desenharEscolas(escolas) {
    if (!escolas.length) {
      lista.innerHTML = `<p style="color:var(--ink-faint);grid-column:1/-1;">Nenhuma escola encontrada com esse nome.</p>`;
      return;
    }

    lista.innerHTML = escolas
      .map((e) => {
        const iniciais = e.nome
          .split(/\s+/)
          .filter(Boolean)
          .slice(0, 2)
          .map((p) => p[0].toUpperCase())
          .join("");
        return `
        <button
          type="button"
          class="escola-card"
          data-escola-id="${e.id}"
        >
          <span class="escola-card-avatar">${iniciais}</span>
          <span class="escola-card-nome">${escapeHtml(e.nome)}</span>
        </button>
      `;
      })
      .join("");

    lista.querySelectorAll("[data-escola-id]").forEach((btn) => {
      const escola = escolas.find((e) => e.id === Number(btn.dataset.escolaId));
      btn.addEventListener("click", () => selecionar(escola));
    });
  }

  try {
    const escolas = await Api.escolas.listar();

    if (!escolas || escolas.length === 0) {
      lista.innerHTML = `<p style="color:var(--ink-faint);grid-column:1/-1;">Nenhuma escola cadastrada no momento. Fale com o suporte.</p>`;
      return;
    }

    // Só mostra a busca quando vale a pena (bastante escola cadastrada).
    if (escolas.length > 6) {
      campoBusca.style.display = "block";
    }

    desenharEscolas(escolas);

    inputBusca.addEventListener("input", () => {
      const termo = inputBusca.value.trim().toLowerCase();
      const filtradas = termo
        ? escolas.filter((e) => e.nome.toLowerCase().includes(termo))
        : escolas;
      desenharEscolas(filtradas);
    });
  } catch (err) {
    erroBox.textContent = err.message || "Não foi possível carregar as escolas.";
    erroBox.classList.add("show");
    lista.innerHTML = "";
  }
}