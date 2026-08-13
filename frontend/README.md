# Enfermaria Escolar — Frontend

Frontend em HTML, CSS e JavaScript puro (sem build, sem dependências para instalar) para o Sistema de Gestão da Enfermaria Escolar. Conversa diretamente com a API em FastAPI já existente no projeto.

## Como rodar

Não precisa de `npm install` nem nada parecido. Basta servir os arquivos estaticamente:

**Opção 1 — VS Code**: instale a extensão "Live Server" e clique em "Go Live" com o `index.html` aberto.

**Opção 2 — Python** (já vem instalado na maioria dos sistemas):
```
cd frontend
python -m http.server 5500
```
Depois acesse `http://localhost:5500` no navegador.

> Não abra o `index.html` direto com duplo clique (protocolo `file://`) — alguns navegadores bloqueiam as requisições nesse modo. Sempre sirva por um servidor local, mesmo que simples como os acima.

## Antes de usar: habilite o CORS no backend

Como o frontend roda em um endereço (ex.: `http://localhost:5500`) diferente do backend (`http://localhost:8000`), o navegador vai bloquear as requisições por padrão. O projeto backend enviado ainda não tem CORS configurado. Adicione isto em `backend/app/main.py`, logo após criar o `app = FastAPI(...)`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # em produção, troque "*" pelo endereço real do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Sem isso, o login e todas as outras telas vão falhar com erro de rede/CORS no console do navegador.

## Configuração do endereço da API

Se o backend rodar em outra porta/host, ajuste em `js/config.js`:
```js
window.APP_CONFIG = {
  API_URL: "http://localhost:8000"
};
```

## Login

Use o usuário criado pelo script `backend/criar_admin.py` (login `admin` / senha `admin123`, salvo se você tiver alterado o script). Os perfis de acesso (`tipo_acesso`) reconhecidos pela interface são `ADMIN`, `ENFERMAGEM` e `PROFESSORA`, com telas e ações mostradas de acordo com o que cada perfil pode fazer na API:

- **ADMIN**: acesso completo, incluindo desativar alunos e salas.
- **ENFERMAGEM**: cadastra alunos, registra atendimentos e gerencia os cadastros de apoio (salas, professoras, equipe, responsáveis, tipos de ocorrência).
- **PROFESSORA**: acesso de consulta ao painel, alunos, atendimentos e relatórios.

## Estrutura de pastas

```
frontend/
├── index.html
├── css/style.css              # design tokens + estilos de toda a aplicação
├── js/
│   ├── config.js               # endereço da API
│   ├── icons.js                 # ícones em SVG (sem emojis)
│   ├── utils.js                 # formatação, toasts, modais
│   ├── auth-store.js            # sessão logada (localStorage)
│   ├── api.js                   # chamadas para a API FastAPI
│   ├── shell.js                 # barra lateral + topo do app
│   ├── router.js                # navegação por #/rota
│   └── pages/                   # uma página por arquivo
│       ├── login.js
│       ├── dashboard.js
│       ├── alunos.js
│       ├── ocorrencias.js
│       ├── cadastros.js
│       └── relatorios.js
└── assets/illustrations/       # ilustrações SVG originais (mascote, tela de login, estado vazio)
```

## O que foi implementado

- Tela de login com token JWT, sessão salva no navegador.
- Painel com indicadores do mês e 4 gráficos (Chart.js) usando os dados de `/dashboard/resumo`.
- Alunos: busca, cadastro, edição, ficha com histórico de atendimentos e download do PDF individual, desativação (admin).
- Atendimentos: listagem com filtros por aluno/período, registro de novo atendimento, detalhe.
- Cadastros: Salas, Professoras, Equipe de enfermagem, Responsáveis e Tipos de ocorrência — cada aba respeita exatamente as operações que a API de cada uma oferece.
- Relatórios: download dos PDFs diário, semanal, mensal e do histórico individual do aluno.
- Design próprio, em azul-claro e branco, com ilustrações desenhadas para o projeto (mascote ursinho, cena da tela de login, estado vazio) — sem emojis e sem bibliotecas de ícones genéricas.
