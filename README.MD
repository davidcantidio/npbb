# NPBB - Sistema de eventos e leads

Plataforma para gestao de eventos, captura de leads, gamificacao e dashboards. O backend e FastAPI/SQLModel e o frontend e React/Vite.

## Arquitetura (6 bullets)
- **Backend**: FastAPI + SQLModel + Alembic (API + regras de negocio).
- **Frontend**: Vite + React + MUI (UI e fluxos).
- **Banco**: Postgres via SQLAlchemy (Supabase).
- **Auth**: JWT (login, /auth/me, recuperacao de senha).
- **Leads**: importacao CSV/XLSX com mapeamento assistido + tabela paginada em `/leads`.
- **Relatorios**: dashboard agregado + geracao de DOCX (Festival TMJ 2025).

## Setup rapido (caminho feliz)

**Banco:** o projeto usa **Supabase** como padrao (`DATABASE_URL` / `DIRECT_URL` no `.env`). PostgreSQL local e opcional.

### Backend — Windows (PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# edite .env e configure DATABASE_URL/DIRECT_URL (Supabase)
cd ..
.\scripts\dev_backend.ps1
```
O script `dev_backend.ps1` ja define `PYTHONPATH` e usa `backend\.venv\Scripts\python.exe` (nao e obrigatorio ativar a venv antes). Para ativar a venv no terminal atual: `.\scripts\activate_backend_venv.ps1`.

Se o PowerShell bloquear scripts (`.ps1`), use uma vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

**PostgreSQL local no Windows (opcional):** instale pelo instalador em https://www.postgresql.org/download/windows/, crie o banco `npbb` e aponte `DATABASE_URL`/`DIRECT_URL` no `.env`.

### Backend — macOS / Linux
```bash
cd backend
# Opcional: Postgres local (macOS/Homebrew)
# brew install python@3.12 postgresql@16
# brew services start postgresql@16
# /opt/homebrew/opt/postgresql@16/bin/createdb npbb
/opt/homebrew/bin/python3.12 -m venv .venv   # macOS/Homebrew; em Linux use: python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# edite .env e configure DATABASE_URL/DIRECT_URL (Supabase)
PYTHONPATH=.. python -m uvicorn app.main:app --reload
# alternativa na raiz: ./scripts/dev_backend.sh
# alternativa em backend/: ./scripts/dev_api.sh
```

## Rodando da raiz do repo

**Linux / macOS (bash):**
```bash
source backend/.venv/bin/activate
./scripts/dev_backend.sh
```

**Windows (PowerShell, na raiz do repo):**
```powershell
.\scripts\dev_backend.ps1
```

**Alternativa tecnica (mesmo efeito do script):**

- bash: `source backend/.venv/bin/activate` e `PYTHONPATH=. uvicorn app.main:app --reload --app-dir backend`
- PowerShell:
```powershell
$env:PYTHONPATH = "$(Get-Location);$(Get-Location)\backend"
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

Importante:
- `uvicorn app.main:app --reload` na raiz, sem `PYTHONPATH` e sem `--app-dir backend`, nao e suportado.

Frontend:
```bash
cd frontend
npm install
# Copie .env: PowerShell: Copy-Item .env.example .env  |  bash: cp .env.example .env
npm run dev
```

## Scraper de redes (ferramenta auxiliar)

Existe um pipeline autonomo (Node/Playwright + Python) para coleta de posts em Instagram/X/TikTok e geracao de indicadores relacionados a mencoes ao BB. Codigo e instrucoes: [tools/mcp-bb-scraping/README.md](tools/mcp-bb-scraping/README.md). As saidas locais ficam em `tools/mcp-bb-scraping/out/` e nao sao versionadas.

## Framework Fabrica

`PROJETOS/COMUM` neste repositório é espelhado da Fabrica. A fonte de verdade operacional fica no clone local em `C:\Users\NPBB\fabrica`.

Comando canônico da CLI da Fabrica para operar o `npbb`:
```powershell
C:\Users\NPBB\fabrica\.venv\Scripts\python.exe C:\Users\NPBB\fabrica\scripts\fabrica.py --repo-root C:\Users\NPBB\npbb --help
```

A CLI carrega automaticamente variáveis de ambiente a partir de `.env` na raiz do npbb e, em seguida, de `backend/.env` (ficheiros gitignored), **sem** substituir variáveis que já estejam definidas no terminal. Use isto para `OPENROUTER_API_KEY`, `FABRICA_FEATURES_PROVIDER_MODEL`, etc.

Para fluxos de sync e pré-validação, defina `FABRICA_PROJECTS_DATABASE_URL` no terminal atual antes de chamar a CLI:
```powershell
$env:FABRICA_PROJECTS_DATABASE_URL = "postgresql://USER:PASS@HOST:5432/DB"
C:\Users\NPBB\fabrica\.venv\Scripts\python.exe C:\Users\NPBB\fabrica\scripts\fabrica.py --repo-root C:\Users\NPBB\npbb sync --dry-run
```

Atualização de `PROJETOS/COMUM` a partir da Fabrica:
```powershell
Get-ChildItem -LiteralPath C:\Users\NPBB\npbb\PROJETOS\COMUM -Force | Remove-Item -Recurse -Force
robocopy "C:\Users\NPBB\fabrica\PROJETOS\COMUM" "C:\Users\NPBB\npbb\PROJETOS\COMUM" /E /COPY:DAT /R:2 /W:1
```

`PROJETOS/NPBB` e os demais projetos da aplicação continuam sendo mantidos apenas no `npbb`.

## Testes
```bash
# backend (com venv ativa, ou use backend/.venv/Scripts/python.exe no Windows)
cd backend
python -m pytest -q
```

Backend com SQLite de teste (como no CI): na pasta `backend`, defina `TESTING=true` e `SECRET_KEY` (veja `docs/SETUP.md` / `AGENTS.md`).

```bash
# frontend
cd frontend
npm test -- --run
npm run lint
npm run typecheck
npx playwright install chromium
npm run test:e2e
```

## E2E oficial (Playwright)
- Runner: `frontend/playwright.config.ts`
- Base: SQLite efemero seedado por `backend/scripts/seed_playwright_smoke.py`
- Usuario seedado: `david.cantidio@npbb.com.br`
- O smoke oficial valida auth/sessao, rotas protegidas, ETL interno, revisao humana, import de leads e hardening de cadastro.
- O script `frontend/scripts/smoke_evento_leads.mjs` permanece como utilitario local de debug API.

Execucao local:
```bash
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
npx playwright install chromium
npm run test:e2e
```

## Deploy (producao)

Stack oficial: **Supabase** (plano pago), **Render** (plano pago) e **Cloudflare Pages** (gratuito).

| Servico | Funcao |
|---------|--------|
| Supabase | Postgres (DATABASE_URL, DIRECT_URL) |
| Render | API FastAPI (`npbb-api`) |
| Cloudflare Pages | Frontend React/Vite |

- **Dominio gratuito:** `https://npbb.pages.dev` (subdominio padrao do Cloudflare Pages).
- **Dominio customizado:** `https://app.npbb.com.br` (requer configuracao DNS).

Guia completo: `docs/DEPLOY_RENDER_CLOUDFLARE.md`. Referencia de configuracao do Render: `docs/render.yaml`.

## Comandos principais
- Backend (raiz): `./scripts/dev_backend.sh` (bash) ou `.\scripts\dev_backend.ps1` (PowerShell)
- Backend (pasta `backend/`): `PYTHONPATH=.. python -m uvicorn app.main:app --reload` (bash) ou, no PowerShell, `$env:PYTHONPATH = ".."; python -m uvicorn app.main:app --reload` (ou `./scripts/dev_api.sh` no Git Bash/WSL)
- Migrations: `alembic upgrade head` (com venv ativa, dentro de `backend/`)
- Seeds (dev): `python -m scripts.seed_domains` / `python -m scripts.seed_sample` (a partir de `backend/`)
- Frontend: `npm run dev`

## Docs
- `docs/INDEX.md` - mapa geral
- `docs/SETUP.md` - setup detalhado
- `docs/WORKFLOWS.md` - importacao, dashboards e relatorios
- `docs/TROUBLESHOOTING.md` - problemas comuns
- `docs/ARCHITECTURE.md` - visao tecnica
- `docs/DEPLOY_RENDER_CLOUDFLARE.md` - deploy oficial (Render + Cloudflare Pages)

## Primeira tarefa (vibe coding)
1) Suba backend + frontend.
2) Acesse `/leads` e faça o preview de um CSV/XLSX pequeno.
3) Abra `/dashboard/leads` para ver KPIs e rankings.
