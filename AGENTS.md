# Cursor Cloud / Agent Instructions

## Overview

NPBB (Núcleo de Patrocínios Banco do Brasil) is an event management and sponsorship analytics platform.

**Architecture:** FastAPI backend (Python 3.12) + React/Vite frontend (TypeScript) + PostgreSQL 16.

## Services

| Service      | Port | How to start                                                                 |
|--------------|------|------------------------------------------------------------------------------|
| PostgreSQL   | 5432 | macOS: `brew services start postgresql@16` — Linux: `sudo pg_ctlcluster 16 main start` |
| Backend      | 8000 | `./scripts/dev_backend.sh` from repo root, or `bash backend/scripts/dev_api.sh` from `backend/` |
| Frontend     | 5173 | `cd frontend && npm run dev`                                                 |

## Key gotchas

- **PYTHONPATH is required** for the backend: imports use `core/` at repo root. Always set `PYTHONPATH` to include both the repo root and `backend/`. The dev scripts (`scripts/dev_backend.sh`, `backend/scripts/dev_api.sh`) handle this automatically.

- **Backend .env**: The `.env` file in `backend/` must have `DATABASE_URL` and `DIRECT_URL` set. The dotenv file is sometimes not picked up by alembic — if migrations fail with "no password supplied", pass `DATABASE_URL` and `DIRECT_URL` as shell env vars explicitly.

- **PostgreSQL auth**: The pg_hba.conf must allow the npbb user. On macOS Homebrew, `createdb npbb` creates the DB; ensure the system user can connect. On Linux, add `host all npbb 127.0.0.1/32 md5` and reload.

- **Backend tests**: Run with `PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` from `backend/`. The `TESTING=true` flag makes the DB module fall back to SQLite (no Postgres needed for tests).

- **Frontend tests**: `cd frontend && npm run test -- --run` (vitest).

- **Lint/typecheck**: See `docs/SETUP.md` "Comandos rapidos" section and `Makefile` `ci-quality` target.

- **Ruff has pre-existing F401 warnings** in the backend codebase; these are not blockers.

- **Seeded dev user**: Create with `ADMIN_EMAIL=david.cantidio@npbb.com.br ADMIN_PASSWORD='Senha123!' python scripts/seed_admin.py` from `backend/`. For `seed_sample.py`, the default password is `SEED_PASSWORD` (default: `Senha123!`).

- **Creating events via API** requires `descricao`, `agencia_id`, `tipo_id`, `subtipo_id`, and `diretoria_id` fields even though the schema marks them as optional — the DB has NOT NULL constraints.
