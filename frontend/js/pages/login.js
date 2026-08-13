// =========================================================
// Pagina de login
// =========================================================

function renderLogin() {
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
          <h2>Bem-vinda(o) de volta</h2>
          <p style="margin-bottom:22px;">Entre com suas credenciais para acessar o sistema.</p>

          <div class="form-error" id="login-error"></div>

          <form id="form-login" novalidate>
            <div class="field">
              <label for="login">Login</label>
              <input type="text" id="login" name="login" autocomplete="username" placeholder="seu.login" required />
            </div>
            <div class="field">
              <label for="senha">Senha</label>
              <input type="password" id="senha" name="senha" autocomplete="current-password" placeholder="••••••••" required />
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;padding:13px;" id="btn-entrar">
              Entrar
            </button>
          </form>
        </div>
      </div>
    </div>
  `;

  const form = document.getElementById("form-login");
  const erroBox = document.getElementById("login-error");
  const btn = document.getElementById("btn-entrar");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    erroBox.classList.remove("show");
    const login = form.login.value.trim();
    const senha = form.senha.value;

    if (!login || !senha) {
      erroBox.textContent = "Preencha o login e a senha para continuar.";
      erroBox.classList.add("show");
      return;
    }

    btn.disabled = true;
    btn.textContent = "Entrando...";

    try {
      const resp = await Api.auth.login(login, senha);

      // Guarda o token antes de buscar o nome completo em /auth/me
      AuthStore.set({
        access_token: resp.access_token,
        usuario: { id: resp.usuario_id, nome: login, login, tipo_acesso: resp.tipo_acesso }
      });

      let usuario;
      try {
        usuario = await Api.auth.me();
      } catch {
        usuario = { id: resp.usuario_id, nome: login, login, tipo_acesso: resp.tipo_acesso };
      }

      AuthStore.set({
        access_token: resp.access_token,
        usuario: {
          id: usuario.id,
          nome: usuario.nome,
          login: usuario.login,
          tipo_acesso: usuario.tipo_acesso
        }
      });
      showToast(`Bem-vinda(o), ${usuario.nome.split(" ")[0]}!`, "success");
      location.hash = "#/dashboard";
    } catch (err) {
      erroBox.textContent = err.message || "Login ou senha inválidos.";
      erroBox.classList.add("show");
    } finally {
      btn.disabled = false;
      btn.textContent = "Entrar";
    }
  });
}
