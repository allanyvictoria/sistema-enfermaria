# Roteiro de Deploy — Sistema de Enfermaria Escolar

Plano 100% gratuito:
- **Banco de dados** → Supabase (PostgreSQL gerenciado, não expira)
- **Backend (FastAPI)** → Render (Docker, plano free)
- **Frontend (HTML/CSS/JS)** → Netlify

O que eu já ajustei no código (não precisa mexer):
- `SECRET_KEY` do login agora vem do `.env`, não fica mais fixa no código.
- CORS do backend agora é configurável por `.env` (`ALLOWED_ORIGINS`).
- `requirements.txt` estava salvo em formato Windows (UTF-16) — convertido para o formato padrão, senão o `pip install` falha no Linux.
- Removi as pastas `venv/` e `__pycache__/` (são geradas automaticamente, não devem ir para o servidor nem para o Git).
- Criei `backend/Dockerfile`, `backend/.env.example` e `backend/.gitignore`.
- Deixei um comentário no `frontend/js/config.js` indicando onde trocar a URL da API depois do deploy.

O que fica por sua conta (senhas e chaves — de propósito, para você controlar):
- Preencher o `.env` de produção com a `SECRET_KEY`, `DATABASE_URL` e `ALLOWED_ORIGINS` reais.
- Trocar a senha padrão do usuário de enfermagem (`enf` / `enf123`) criada pelo `criar_admin.py`.

---

## Parte 1 — Colocar o código no GitHub

1. Crie uma conta em https://github.com (se ainda não tiver).
2. Crie um repositório novo, ex: `sistema-enfermaria`. Pode ser privado.
3. No seu computador, dentro da pasta do projeto (a que eu te devolvi), rode:
   ```
   git init
   git add .
   git commit -m "Primeira versão"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/sistema-enfermaria.git
   git push -u origin main
   ```
4. Confirme no GitHub que a pasta `backend/venv` **não** subiu (o `.gitignore` que criei impede isso). Se você não usar Git ainda, me avisa que te explico do zero.

---

## Parte 2 — Criar o banco de dados (Supabase)

1. Vá em https://supabase.com e crie uma conta gratuita.
2. Clique em **New Project**.
   - Dê um nome (ex: `enfermaria`).
   - Crie uma **senha do banco** (guarde essa senha, você vai usar já já).
   - Escolha a região mais próxima (ex: South America - São Paulo, se disponível).
3. Espere o projeto terminar de ser criado (leva 1–2 minutos).
4. No menu lateral, vá em **SQL Editor** → **New query**.
5. Abra o arquivo `banco/estrutura.sql` do projeto, copie todo o conteúdo, cole no editor do Supabase e clique em **Run**. Isso cria todas as tabelas.
6. Se o arquivo `banco/enviar.sql` tiver dados iniciais que você quer importar, repita o passo com ele.
7. Agora pegue a string de conexão: vá em **Project Settings** → **Database** → **Connection string** → escolha o modo **URI**. Vai ser algo como:
   ```
   postgresql://postgres:[SUA-SENHA]@db.xxxxxxxx.supabase.co:5432/postgres
   ```
8. Guarde essa URL completa (com a senha já dentro) — vai ser o valor de `DATABASE_URL` no próximo passo.

---

## Parte 3 — Deploy do backend (Render)

1. Vá em https://render.com e crie uma conta (dá para entrar direto com GitHub).
2. Clique em **New** → **Web Service**.
3. Conecte seu repositório `sistema-enfermaria` do GitHub.
4. Configurações do serviço:
   - **Root Directory**: `backend`
   - **Environment**: **Docker** (o Render vai detectar o `Dockerfile` que criei automaticamente)
   - **Instance Type**: **Free**
5. Em **Environment Variables**, adicione três variáveis:
   | Nome | Valor |
   |---|---|
   | `DATABASE_URL` | a string de conexão do Supabase (Parte 2, passo 7) |
   | `SECRET_KEY` | uma chave aleatória forte — gere uma rodando `python -c "import secrets; print(secrets.token_hex(32))"` no seu computador, ou use um gerador de senha online de 64 caracteres |
   | `ALLOWED_ORIGINS` | por enquanto pode deixar `*` — depois que o frontend estiver no ar (Parte 4), volte aqui e troque pela URL do Netlify, ex: `https://enfermaria.netlify.app` |
6. Clique em **Create Web Service**. O Render vai buildar a imagem Docker e subir o serviço — acompanhe os logs.
7. Quando terminar, você vai ter uma URL pública, algo como:
   ```
   https://enfermaria-backend.onrender.com
   ```
8. Teste abrindo essa URL no navegador — deve aparecer:
   ```json
   {"mensagem": "Sistema de Gestão da Enfermaria Escolar"}
   ```

**Nota sobre o plano free do Render:** o serviço "dorme" depois de 15 minutos sem uso e demora de 30 a 60 segundos para acordar na próxima chamada. Para um sistema de uso interno da escola, isso costuma ser aceitável — só avisa a quem for usar que a primeira tela pode demorar um pouco a carregar depois de um tempo parado.

---

## Parte 4 — Deploy do frontend (Netlify)

1. Antes de publicar, abra `frontend/js/config.js` e troque a URL para a do backend que você acabou de publicar:
   ```js
   window.APP_CONFIG = {
     API_URL: "https://enfermaria-backend.onrender.com"
   };
   ```
   Salve, faça commit e push dessa alteração para o GitHub.
2. Vá em https://netlify.com e crie uma conta (também dá para usar o GitHub).
3. Clique em **Add new site** → **Import an existing project** → conecte o mesmo repositório.
4. Configurações do site:
   - **Base directory**: `frontend`
   - **Build command**: deixe em branco (não tem build, é HTML puro)
   - **Publish directory**: `frontend`
5. Clique em **Deploy site**. Em cerca de 1 minuto você recebe uma URL pública, tipo:
   ```
   https://enfermaria.netlify.app
   ```

---

## Parte 5 — Fechar o ciclo (CORS e segurança)

1. Volte no Render, na configuração do backend, e edite a variável `ALLOWED_ORIGINS` para a URL real do Netlify (Parte 4, passo 5). Isso impede que qualquer site na internet chame sua API.
2. Crie o usuário de enfermagem no banco de produção. No Render, abra o **Shell** do serviço (aba "Shell") e rode:
   ```
   python criar_admin.py
   ```
   Isso cria o login `enf` / senha `enf123`.
3. **Troque essa senha imediatamente** depois do primeiro login — ela está em texto aberto no código-fonte, então não é segura para uso real.
4. Acesse `https://enfermaria.netlify.app` (sua URL do Netlify) e teste o login.

---

## Checklist final

- [ ] Código no GitHub (sem `venv/`, sem `.env` real)
- [ ] Banco criado no Supabase, com `estrutura.sql` importado
- [ ] Backend no ar no Render, respondendo na URL pública
- [ ] `SECRET_KEY` de produção definida (diferente da de desenvolvimento)
- [ ] Frontend no ar no Netlify, apontando para a URL do backend
- [ ] `ALLOWED_ORIGINS` no Render restrito à URL do Netlify (não mais `*`)
- [ ] Usuário `enf` criado e senha padrão trocada

Qualquer erro que aparecer nos logs do Render ou do navegador (aba Console, F12), me manda a mensagem que eu te ajudo a resolver.
