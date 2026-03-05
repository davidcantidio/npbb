# AGENTS.md

## Cursor Cloud specific instructions

### Overview

NPBB is a Brazilian event management and lead capture platform. It has a FastAPI backend (Python 3.12) and a React/Vite frontend (TypeScript). See `docs/SETUP.md` for full setup instructions.

### Important: DATABASE_URL environment variable

The cloud VM may have a `DATABASE_URL` secret injected as an environment variable that points to a remote PostgreSQL instance. The backend's `load_dotenv()` does **not** override existing env vars, so the `.env` file value is ignored when the env var is already set. You **must** unset `DATABASE_URL` and `DIRECT_URL` before starting the backend dev server or running seeds/init scripts locally:

```bash
env -u DATABASE_URL -u DIRECT_URL <command>
```

For tests, this is not an issue because pytest triggers the SQLite fallback automatically.

### Running services

- **Backend**: `env -u DATABASE_URL -u DIRECT_URL bash -c 'source backend/.venv/bin/activate && PYTHONPATH=/workspace:/workspace/backend uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000'`
- **Frontend**: `cd frontend && npm run dev` (serves on `http://127.0.0.1:5173`, proxies `/api` to backend)

### Running tests

- **Backend tests**: `cd backend && source .venv/bin/activate && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key python -m pytest -q` (auto-uses SQLite)
- **Frontend tests**: `cd frontend && npm run test -- --run`
- **Frontend lint**: `cd frontend && npm run lint`
- **Frontend typecheck**: `cd frontend && npm run typecheck`
- **Backend lint**: `cd backend && source .venv/bin/activate && ruff check app tests`

### Dev database

The backend `.env` is configured with `DATABASE_URL=sqlite:////workspace/backend/dev.db`. Tables are created via `init_db()` — run once after setup:

```bash
cd backend && env -u DATABASE_URL -u DIRECT_URL bash -c 'source .venv/bin/activate && PYTHONPATH=/workspace:/workspace/backend python -c "import app.models.models; from app.db.database import init_db; init_db()"'
```

After creating tables, seed domain reference data (required for event creation):

```bash
cd backend && env -u DATABASE_URL -u DIRECT_URL bash -c 'source .venv/bin/activate && PYTHONPATH=/workspace:/workspace/backend python -m scripts.seed_domains'
```

### Seed scripts

Run seed scripts as modules from `backend/` directory with `-m` flag (e.g. `python -m scripts.seed_domains`). Running them as scripts directly fails due to relative imports.

### CI quality gate

`make ci-quality` runs the full CI quality gate (lint + typecheck + tests + build + architecture guards). See `Makefile` for details.
