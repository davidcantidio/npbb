# Deploy: Render (API) + Cloudflare Pages (Frontend)

Guia oficial para publicar o NPBB: backend FastAPI no Render e frontend React/Vite no Cloudflare Pages. O banco de dados e o Postgres do Supabase (plano pago).

## Dominio publico de producao

- Hostname canonico de go-live do frontend publico: `https://app.npbb.com.br`
- `PUBLIC_APP_BASE_URL` e `FRONTEND_ORIGIN` devem apontar para esse dominio em producao.
- O hostname `*.pages.dev` pode existir como endereco tecnico do Cloudflare Pages, mas nao deve ser tratado como URL publica canonica dos QR codes e links de landing.

## 1) Backend no Render

Crie um Web Service no Render com:

- Name: `npbb-api`
- Repository: `davidcantidio/npbb`
- Branch: `main`
- Root Directory: `backend`
- Runtime: `Python 3.12`
- Build Command: `pip install -r requirements.txt`
- Start Command: `bash -lc "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"`
- Health Check Path: `/health`

### Variaveis obrigatorias (Render)

- `DATABASE_URL` (Supabase)
- `DIRECT_URL` (Supabase)
- `SECRET_KEY`
- `PYTHONPATH` (obrigatorio para imports de `core/`): `/opt/render/project/src:/opt/render/project/src/backend`
- `FRONTEND_ORIGIN=https://app.npbb.com.br`
- `PUBLIC_APP_BASE_URL=https://app.npbb.com.br`
- `EMAIL_BACKEND=console`

### Variaveis recomendadas (Render)

- `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- `PASSWORD_RESET_URL=https://app.npbb.com.br/reset-password`
- `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=60`
- `PASSWORD_RESET_TOKEN_SECRET`
- `SQL_ECHO=false`
- `PUBLIC_LANDING_BASE_URL` (opcional; base publica do backend)
- `PUBLIC_API_DOC_URL` (opcional; ex.: `https://npbb-api.onrender.com/docs`)

### Validacao backend

- `GET https://npbb-api.onrender.com/health` deve retornar `{"status":"ok"}`
- `GET https://npbb-api.onrender.com/docs` deve responder `200`

### Estado operacional validado (F3)

O runtime do backend foi validado contra o Supabase como banco unico (ISSUE-F3-01-001):
- Boot com `DATABASE_URL` do Supabase (conexao direta ou pooler)
- Endpoint `/health` responde `{"status":"ok"}`
- Endpoints que consultam o banco (ex.: `/eventos/{id}/landing`) retornam dados do Supabase

## 2) Frontend no Cloudflare Pages

Crie um projeto Pages com:

- Project name: `npbb`
- Repository: `davidcantidio/npbb`
- Production branch: `main`
- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`

### Variaveis obrigatorias (Pages)

- `NODE_VERSION=20`
- `VITE_API_BASE_URL=https://npbb-api.onrender.com`

### Fallback SPA

O arquivo abaixo deve existir para evitar 404 em rotas de SPA:

- `frontend/public/_redirects`
- Conteudo: `/* /index.html 200`

### Validacao frontend

- `https://app.npbb.com.br` abre a tela de login
- abrir `https://app.npbb.com.br/eventos` nao retorna 404
- requests do frontend apontam para `https://npbb-api.onrender.com`

## 3) Checklist pre-go-live

Execute este checklist antes de liberar QR codes, links publicos ou campanhas em producao:

- [ ] O dominio customizado do frontend esta ativo e respondendo em `https://app.npbb.com.br`
- [ ] `PUBLIC_APP_BASE_URL=https://app.npbb.com.br`
- [ ] `FRONTEND_ORIGIN=https://app.npbb.com.br`
- [ ] `PASSWORD_RESET_URL=https://app.npbb.com.br/reset-password`
- [ ] `VITE_API_BASE_URL` aponta para a API de producao
- [ ] O hostname `*.pages.dev` nao esta sendo usado como URL publica canonica do app
- [ ] Smoke test manual: abrir uma landing publica ou QR gerado e confirmar que o hostname final e `app.npbb.com.br`

Regra de bloqueio:
- Nao seguir com o go-live se `PUBLIC_APP_BASE_URL` estiver ausente, apontando para
  `localhost`, `127.0.0.1`, `*.pages.dev` ou qualquer hostname provisorio. Nesse
  cenario, QR codes e links publicos podem ser gerados com URL incorreta.

## 4) Pos-deploy

Se o nome final da API, do dominio customizado ou do projeto Pages mudar:

1. Atualize no Render:
   - `FRONTEND_ORIGIN`
   - `PUBLIC_APP_BASE_URL`
   - `PASSWORD_RESET_URL`
2. Atualize no Pages:
   - `VITE_API_BASE_URL`
3. Confirme que o dominio customizado continua sendo `app.npbb.com.br`.
4. Redeploy backend e frontend.
