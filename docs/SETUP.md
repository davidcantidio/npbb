# Setup (Backend + Frontend)

Este guia cobre o setup completo. Se quiser apenas o caminho feliz, veja o README.

## TL;DR (caminho feliz)
```bash
# backend
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload

# frontend (em outro terminal)
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Pre-requisitos
- Python **3.12**
- Node.js **18+**
- Postgres (ou Supabase)

## Backend
### 1) Criar ambiente virtual e instalar deps
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 2) Variaveis de ambiente
Crie o arquivo `.env`:
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
```

Exemplo (sem PII, substitua pelos seus valores):
```env
DATABASE_URL="postgresql+psycopg2://user:password@host:5432/postgres?sslmode=require"
DIRECT_URL="postgresql+psycopg2://user:password@host:5432/postgres?sslmode=require"
SECRET_KEY="change-me"
FRONTEND_ORIGIN="http://localhost:5173"
EMAIL_BACKEND="console"
PASSWORD_RESET_DEBUG="false"
```

Observacoes:
- `DATABASE_URL` e a conexao usada pela API.
- `DIRECT_URL` e a conexao direta para migrations/seed (recomendado no Supabase).
- O backend aceita variaveis separadas (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`) como fallback.
- Em testes, o backend permite SQLite se `TESTING=true` ou `PYTEST_CURRENT_TEST` estiver setado.

### 3) Rodar a API
```bash
python -m uvicorn app.main:app --reload
```

### 4) Migrations (dev)
```bash
alembic upgrade head
```

### 5) Seeds (opcional)
```bash
python scripts/seed_domains.py
python scripts/seed_sample.py
```

## Frontend
### 1) Instalar deps
```bash
cd frontend
npm install
```

### 2) Variaveis de ambiente
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
```

Exemplo:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3) Rodar o front
```bash
npm run dev
```

## Comandos rapidos
- Backend: `python -m uvicorn app.main:app --reload`
- Tests (backend): `python -m pytest -q`
- Tests (frontend): `npm test -- --run`
- Lint (frontend): `npm run lint`
- Typecheck (frontend): `npm run typecheck`

## TODO (nao encontrado no repo)
- Ambiente docker-compose para subir tudo localmente.
