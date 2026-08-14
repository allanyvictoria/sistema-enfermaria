// =========================================================
// Cliente de acesso a API (FastAPI) do Sistema de Enfermaria
// =========================================================

class ApiError extends Error {
  constructor(mensagem, status) {
    super(mensagem);
    this.status = status;
  }
}

async function apiRequest(caminho, { method = "GET", body, autenticado = true, blob = false } = {}) {
  const headers = {};
  if (!blob) headers["Content-Type"] = "application/json";

  if (autenticado) {
    const token = AuthStore.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let resposta;
  try {
    resposta = await fetch(`${window.APP_CONFIG.API_URL}${caminho}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined
    });
  } catch (erroRede) {
    throw new ApiError(
      "Não foi possível conectar ao servidor da enfermaria. Verifique se o backend está rodando e se o endereço em js/config.js está correto.",
      0
    );
  }

  if (resposta.status === 401 && autenticado) {
    AuthStore.clear();
    if (location.hash !== "#/login") {
      location.hash = "#/login";
    }
    throw new ApiError("Sessão expirada. Faça login novamente.", 401);
  }

  if (!resposta.ok) {
    let detalhe = "Ocorreu um erro ao falar com o servidor.";
    try {
      const dados = await resposta.json();
      if (dados?.detail) {
        detalhe = typeof dados.detail === "string" ? dados.detail : JSON.stringify(dados.detail);
      }
    } catch {}
    throw new ApiError(detalhe, resposta.status);
  }

  if (blob) return resposta.blob();
  if (resposta.status === 204) return null;

  const texto = await resposta.text();
  return texto ? JSON.parse(texto) : null;
}

const Api = {
  escolas: {
    listar: () => apiRequest("/escolas", { autenticado: false })
  },
  auth: {
    login: (login, senha, escolaId) => apiRequest("/auth/login", { method: "POST", body: { login, senha, escola_id: escolaId }, autenticado: false }),
    me: () => apiRequest("/auth/me")
  },
  dashboard: {
    resumo: () => apiRequest("/dashboard/resumo")
  },
  alunos: {
    listar: () => apiRequest("/alunos/"),
    buscar: (id) => apiRequest(`/alunos/${id}`),
    historico: (id) => apiRequest(`/alunos/${id}/historico`),
    criar: (dados) => apiRequest("/alunos/", { method: "POST", body: dados }),
    atualizar: (id, dados) => apiRequest(`/alunos/${id}`, { method: "PUT", body: dados }),
    desativar: (id) => apiRequest(`/alunos/${id}`, { method: "DELETE" })
  },
  ocorrencias: {
    listar: (filtros = {}) => {
      const params = new URLSearchParams();
      if (filtros.aluno_id) params.set("aluno_id", filtros.aluno_id);
      if (filtros.data_inicio) params.set("data_inicio", filtros.data_inicio);
      if (filtros.data_fim) params.set("data_fim", filtros.data_fim);
      const qs = params.toString();
      return apiRequest(`/ocorrencias/${qs ? "?" + qs : ""}`);
    },
    buscar: (id) => apiRequest(`/ocorrencias/${id}`),
    criar: (dados) => apiRequest("/ocorrencias/", { method: "POST", body: dados })
  },
  salas: {
    listar: () => apiRequest("/salas/"),
    criar: (dados) => apiRequest("/salas/", { method: "POST", body: dados }),
    atualizar: (id, dados) => apiRequest(`/salas/${id}`, { method: "PUT", body: dados }),
    desativar: (id) => apiRequest(`/salas/${id}`, { method: "DELETE" })
  },
  turmas: {
    listar: () => apiRequest("/turmas/"),
    criar: (dados) => apiRequest("/turmas/", { method: "POST", body: dados })
  },
  matriculas: {
    criar: (dados) => apiRequest("/matriculas/", { method: "POST", body: dados })
  },
  professoras: {
    listar: () => apiRequest("/professoras/"),
    criar: (dados) => apiRequest("/professoras/", { method: "POST", body: dados }),
    atualizar: (id, dados) => apiRequest(`/professoras/${id}`, { method: "PUT", body: dados }),
    desativar: (id) => apiRequest(`/professoras/${id}`, { method: "DELETE" }),
    vincular: (id, turmaId) => apiRequest(`/professoras/${id}/vincular/${turmaId}`, { method: "POST" }),
    desvincular: (id, turmaId) => apiRequest(`/professoras/${id}/vincular/${turmaId}`, { method: "DELETE" })
  },
  profissionais: {
    listar: () => apiRequest("/profissionais/"),
    criar: (dados) => apiRequest("/profissionais/", { method: "POST", body: dados })
  },
  responsaveis: {
    listar: () => apiRequest("/responsaveis/"),
    buscar: (id) => apiRequest(`/responsaveis/${id}`),
    criar: (dados) => apiRequest("/responsaveis/", { method: "POST", body: dados }),
    vincular: (id, alunoId) => apiRequest(`/responsaveis/${id}/vincular/${alunoId}`, { method: "POST" }),
    desvincular: (id, alunoId) => apiRequest(`/responsaveis/${id}/vincular/${alunoId}`, { method: "DELETE" })
  },
  usuarios: {
    listar: () => apiRequest("/usuarios/"),
    criar: (dados) => apiRequest("/usuarios/", { method: "POST", body: dados }),
    atualizar: (id, dados) => apiRequest(`/usuarios/${id}`, { method: "PUT", body: dados }),
    desativar: (id) => apiRequest(`/usuarios/${id}`, { method: "DELETE" })
  },
  tiposOcorrencia: {
    listar: () => apiRequest("/tipos-ocorrencia/"),
    criar: (dados) => apiRequest("/tipos-ocorrencia/", { method: "POST", body: dados })
  },
  relatorios: {
    diario: (data) => apiRequest(`/relatorios/diario${data ? "?data=" + data : ""}`, { blob: true }),
    semanal: (dataInicio) => apiRequest(`/relatorios/semanal${dataInicio ? "?data_inicio=" + dataInicio : ""}`, { blob: true }),
    mensal: (mes, ano) => apiRequest(`/relatorios/mensal?mes=${mes}&ano=${ano}`, { blob: true }),
    aluno: (id) => apiRequest(`/relatorios/aluno/${id}`, { blob: true })
  }
};

window.Api = Api;