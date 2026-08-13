// =========================================================
// Estado de autenticacao (persistido em localStorage)
// =========================================================

const AUTH_KEY = "enfermaria_auth";

const AuthStore = {
  get() {
    try {
      const raw = localStorage.getItem(AUTH_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  set(dados) {
    localStorage.setItem(AUTH_KEY, JSON.stringify(dados));
  },
  clear() {
    localStorage.removeItem(AUTH_KEY);
  },
  getToken() {
    const a = this.get();
    return a ? a.access_token : null;
  },
  getUsuario() {
    const a = this.get();
    return a ? a.usuario : null;
  },
  isLogado() {
    return !!this.getToken();
  },
  temPerfil(...perfis) {
    const u = this.getUsuario();
    return !!u && perfis.includes(u.tipo_acesso);
  }
};
