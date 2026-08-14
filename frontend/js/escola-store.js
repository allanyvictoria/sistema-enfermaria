// =========================================================
// Estado da escola selecionada (persistido em localStorage)
// Fica separado do AuthStore de propósito: a escola escolhida
// sobrevive ao logout, então quem sai e entra de novo não
// precisa escolher a escola outra vez — só se clicar em
// "Trocar escola" na tela de login.
// =========================================================

const ESCOLA_KEY = "enfermaria_escola";

const EscolaStore = {
  get() {
    try {
      const raw = localStorage.getItem(ESCOLA_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  set(escola) {
    // Guarda só o essencial (id e nome) pra exibir na tela de login.
    localStorage.setItem(ESCOLA_KEY, JSON.stringify({ id: escola.id, nome: escola.nome }));
  },
  clear() {
    localStorage.removeItem(ESCOLA_KEY);
  },
  getId() {
    const e = this.get();
    return e ? e.id : null;
  },
  isSelecionada() {
    return !!this.getId();
  }
};
