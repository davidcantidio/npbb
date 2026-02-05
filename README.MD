# NPBB - Sistema de eventos e leads

Plataforma para gestao de eventos, captura de leads, gamificacao e dashboards. O backend e FastAPI/SQLModel e o frontend e React/Vite.

## Arquitetura (6 bullets)
- **Backend**: FastAPI + SQLModel + Alembic (API + regras de negocio).
- **Frontend**: Vite + React + MUI (UI e fluxos).
- **Banco**: Postgres (Supabase) via SQLAlchemy.
- **Auth**: JWT (login, /auth/me, recuperacao de senha).
- **Leads**: importacao CSV/XLSX com mapeamento assistido.
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

## Primeira tarefa (vibe coding)
1) Suba backend + frontend.
2) Acesse `/leads` e faça o preview de um CSV/XLSX pequeno.
3) Abra `/dashboard/leads` para ver KPIs e rankings.
