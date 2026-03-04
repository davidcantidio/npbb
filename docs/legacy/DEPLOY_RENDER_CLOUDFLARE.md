# Legacy Deploy: Render (API) + Cloudflare Pages (Frontend)

> Status: legado. O caminho oficial do projeto agora e o deploy em VPS descrito em [DEPLOY_HOSTINGER_VPS.md](/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/docs/DEPLOY_HOSTINGER_VPS.md).

Este guia publica o backend FastAPI primeiro (Render) e depois o frontend React/Vite (Cloudflare Pages), usando os dominios padrao (`onrender.com` e `pages.dev`).

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

- `DATABASE_URL`
- `DIRECT_URL`
- `SECRET_KEY`
- `FRONTEND_ORIGIN=https://npbb.pages.dev`
- `PUBLIC_APP_BASE_URL=https://npbb.pages.dev`
- `EMAIL_BACKEND=console`

### Variaveis recomendadas (Render)

- `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- `PASSWORD_RESET_URL=https://npbb.pages.dev/reset-password`
- `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=60`
- `PASSWORD_RESET_TOKEN_SECRET`
- `SQL_ECHO=false`
- `PUBLIC_LANDING_BASE_URL` (opcional; base publica do backend)
- `PUBLIC_API_DOC_URL` (opcional; ex.: `https://npbb-api.onrender.com/docs`)

### Validacao backend

- `GET https://npbb-api.onrender.com/health` deve retornar `{"status":"ok"}`
- `GET https://npbb-api.onrender.com/docs` deve responder `200`

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

- `https://npbb.pages.dev` abre a tela de login
- abrir `https://npbb.pages.dev/eventos` nao retorna 404
- requests do frontend apontam para `https://npbb-api.onrender.com`

## 3) Pos-deploy

Se o nome final da API ou do Pages mudar:

1. Atualize no Render:
   - `FRONTEND_ORIGIN`
   - `PUBLIC_APP_BASE_URL`
   - `PASSWORD_RESET_URL`
2. Atualize no Pages:
   - `VITE_API_BASE_URL`
3. Redeploy backend e frontend.
