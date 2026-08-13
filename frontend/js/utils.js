// =========================================================
// Utilidades gerais: formatacao, toasts e helpers de DOM
// =========================================================

function formatarData(valor) {
  if (!valor) return "-";
  const d = new Date(valor);
  if (isNaN(d)) return "-";
  return d.toLocaleDateString("pt-BR");
}

function formatarDataHora(valor) {
  if (!valor) return "-";
  const d = new Date(valor);
  if (isNaN(d)) return "-";
  return d.toLocaleDateString("pt-BR") + " às " + d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function calcularIdade(dataNascimento) {
  if (!dataNascimento) return "-";
  const nasc = new Date(dataNascimento);
  if (isNaN(nasc)) return "-";
  const hoje = new Date();
  let idade = hoje.getFullYear() - nasc.getFullYear();
  const m = hoje.getMonth() - nasc.getMonth();
  if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--;
  return idade + " anos";
}

function iniciais(nome) {
  if (!nome) return "?";
  const partes = nome.trim().split(/\s+/);
  const a = partes[0]?.[0] || "";
  const b = partes.length > 1 ? partes[partes.length - 1][0] : "";
  return (a + b).toUpperCase();
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function hoje_isoDate() {
  const d = new Date();
  const off = d.getTimezoneOffset();
  const local = new Date(d.getTime() - off * 60000);
  return local.toISOString().slice(0, 10);
}

// ---------------- Toasts ----------------
function toastContainer() {
  let el = document.getElementById("toast-wrap");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast-wrap";
    el.className = "toast-wrap";
    document.body.appendChild(el);
  }
  return el;
}

const ICON_OK = `<svg viewBox="0 0 24 24" fill="none"><path d="M4 12.5 9.5 18 20 6.5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ICON_ERR = `<svg viewBox="0 0 24 24" fill="none"><path d="M12 8v5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><circle cx="12" cy="16.2" r="1.1" fill="currentColor"/><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/></svg>`;

function showToast(mensagem, tipo = "success") {
  const wrap = toastContainer();
  const el = document.createElement("div");
  el.className = `toast ${tipo}`;
  el.innerHTML = `${tipo === "success" ? ICON_OK : ICON_ERR}<span>${escapeHtml(mensagem)}</span>`;
  wrap.appendChild(el);
  setTimeout(() => {
    el.style.transition = "opacity .25s ease, transform .25s ease";
    el.style.opacity = "0";
    el.style.transform = "translateX(20px)";
    setTimeout(() => el.remove(), 250);
  }, 3600);
}

// ---------------- Modal ----------------
function fecharModal() {
  const overlay = document.getElementById("modal-overlay");
  if (overlay) overlay.remove();
  document.body.style.overflow = "";
}

function abrirModal({ titulo, corpoHtml, wide = false, onMount }) {
  fecharModal();
  document.body.style.overflow = "hidden";
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.id = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal ${wide ? "modal-wide" : ""}">
      <div class="modal-head">
        <h2>${escapeHtml(titulo)}</h2>
        <button class="modal-close" type="button" aria-label="Fechar">✕</button>
      </div>
      <div class="modal-body">${corpoHtml}</div>
    </div>
  `;
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) fecharModal();
  });
  overlay.querySelector(".modal-close").addEventListener("click", fecharModal);
  document.body.appendChild(overlay);
  if (onMount) onMount(overlay);
  return overlay;
}

// ---------------- Confirmacao ----------------
function confirmarAcao({ titulo, mensagem, corLabel = "Confirmar", onConfirm }) {
  abrirModal({
    titulo,
    corpoHtml: `
      <p>${escapeHtml(mensagem)}</p>
      <div class="modal-actions">
        <button class="btn btn-soft" id="cancelar-acao" type="button">Cancelar</button>
        <button class="btn btn-danger" id="confirmar-acao" type="button">${escapeHtml(corLabel)}</button>
      </div>
    `,
    onMount: (overlay) => {
      overlay.querySelector("#cancelar-acao").addEventListener("click", fecharModal);
      overlay.querySelector("#confirmar-acao").addEventListener("click", async () => {
        await onConfirm();
        fecharModal();
      });
    }
  });
}

function loaderHtml(texto = "Carregando informações...") {
  return `<div class="loader-wrap"><div class="spinner"></div><p>${escapeHtml(texto)}</p></div>`;
}

function emptyStateHtml(titulo, texto) {
  return `
    <div class="empty-state">
      <img src="assets/illustrations/empty.svg" alt="" />
      <h3>${escapeHtml(titulo)}</h3>
      <p>${escapeHtml(texto)}</p>
    </div>
  `;
}

function baixarBlob(blob, nomeArquivo) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
