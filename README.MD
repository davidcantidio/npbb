# NPBB - Sistema de eventos e leads

Plataforma para gestao de eventos, captura de leads, gamificacao e dashboards. O backend e FastAPI/SQLModel e o frontend e React/Vite.

## Arquitetura (6 bullets)
- **Backend**: FastAPI + SQLModel + Alembic (API + regras de negocio).
- **Frontend**: Vite + React + MUI (UI e fluxos).
- **Banco**: Postgres via SQLAlchemy (Supabase ou Postgres local na VPS).
- **Auth**: JWT (login, /auth/me, recuperacao de senha).
- **Leads**: importacao CSV/XLSX com mapeamento assistido + tabela paginada em `/leads`.
- **Relatorios**: dashboard agregado + geracao de DOCX (Festival TMJ 2025).

## Setup rapido (caminho feliz)
Backend:
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
# edite .env e configure DATABASE_URL
python -m uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
npm run dev
```

## Testes
```bash
# backend
cd backend
python -m pytest -q

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

## Comandos principais
- Backend: `python -m uvicorn app.main:app --reload`
- Migrations: `alembic upgrade head`
- Seeds (dev): `python scripts/seed_domains.py` / `python scripts/seed_sample.py`
- Frontend: `npm run dev`

## Docs
- `docs/INDEX.md` - mapa geral
- `docs/SETUP.md` - setup detalhado
- `docs/WORKFLOWS.md` - importacao, dashboards e relatorios
- `docs/TROUBLESHOOTING.md` - problemas comuns
- `docs/ARCHITECTURE.md` - visao tecnica
- `docs/DEPLOY_HOSTINGER_VPS.md` - deploy oficial na VPS com Docker Compose
- `docs/RUNBOOK_RESTORE_POSTGRES_VPS.md` - restore de dump e cutover de banco
- `docs/DEPLOY_RENDER_CLOUDFLARE.md` - fluxo legado de deploy publico

## Primeira tarefa (vibe coding)
1) Suba backend + frontend.
2) Acesse `/leads` e faça o preview de um CSV/XLSX pequeno.
3) Abra `/dashboard/leads` para ver KPIs e rankings.
