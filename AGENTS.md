# AGENTS.md

## Cursor Cloud specific instructions

### Overview

NPBB is an event management and marketing analytics platform with a **Python/FastAPI backend** and a **React/Vite frontend**. See `docs/SETUP.md` for the canonical setup guide.

### Services

| Service | Port | How to run |
|---------|------|------------|
| PostgreSQL 16 | 5432 | `sudo pg_ctlcluster 16 main start` |
| Backend (FastAPI) | 8000 | `./scripts/dev_backend.sh` (from repo root) |
| Frontend (Vite) | 5173 | `npm run dev` (from `frontend/`) |

### Gotchas

- **PYTHONPATH is required** for the backend. The `core/` package lives at the repo root. The `dev_backend.sh` and `dev_api.sh` scripts set this automatically. If running manually: `PYTHONPATH=/workspace:/workspace/backend`.
- **Backend `.env` must have real DATABASE_URL values**. The `load_dotenv` in `alembic/env.py` and `app/` reads from `backend/.env`, but when running from repo root, environment variables set inline take precedence. For alembic migrations, prefer setting `DATABASE_URL` and `DIRECT_URL` as env vars explicitly.
- **Backend tests use SQLite fallback** when `TESTING=true` or `PYTEST_CURRENT_TEST` is set. Run with: `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q`.
- **Seed scripts must run as modules** from `backend/`: `cd backend && python -m scripts.seed_domains` (not `python scripts/seed_domains.py`).
- **Ruff lint** has pre-existing warnings (19 unused-import errors in test files). This is a known state of the repo.
- **3 pytest failures** in `test_leads_import_etl_usecases.py` are pre-existing (a `strict` keyword argument mismatch).
- **PostgreSQL auth**: on fresh setup, you need to configure `pg_hba.conf` to use `md5` auth (default Ubuntu installs use `peer`).

### Quick commands reference

See `docs/SETUP.md` for full details and `Makefile` target `ci-quality` for the full CI checks.
