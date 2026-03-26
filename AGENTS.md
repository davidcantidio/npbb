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
- **"Validação executável falhou por ambiente"**: o Cursor valida comandos antes de executar. Se o shell não tiver `python` no PATH (comum no macOS, que tem só `python3`), a validação falha. **Mitigação**: (1) selecione o interpretador correto em Cmd+Shift+P → "Python: Select Interpreter" → `backend/.venv/bin/python`; (2) ou use `backend/.venv/bin/python` explicitamente nos comandos; (3) ou ative o venv antes: `source backend/.venv/bin/activate`. O `.vscode/settings.json` já aponta para `backend/.venv/bin/python` (macOS/Linux); no Windows use `backend/.venv/Scripts/python.exe`.

### Quick commands reference

See `docs/SETUP.md` for full details and `Makefile` target `ci-quality` for the full CI checks.

## OpenClaw governance

- `PROJETOS/COMUM/boot-prompt.md` is the canonical autonomous entrypoint for the local OpenClaw governance flow.
- `PROJETOS/COMUM/SESSION-MAPA.md` is the canonical interactive entrypoint.
- The active governance chain in this repo is `Intake -> PRD -> Feature -> User Story -> Task -> Execucao -> Review -> Auditoria de Feature`.
- `PROJETOS/**/*.md` is the source of truth for governance artifacts. The derived index under `.openclaw/openclaw-projects.sqlite` is read-only operational state.
- New project work must use the canonical layout `PROJETOS/<PROJETO>/features/FEATURE-*/user-stories/US-*/TASK-*.md`.
