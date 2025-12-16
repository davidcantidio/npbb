# NPBB - Sistema de gestao de eventos

Este repositorio contem:
- **backend** em FastAPI/SQLModel (API + regras de negocio)
- **frontend** em Vite/React/MUI (login/cadastro e modulo Eventos)
- **docs** com especificacoes de telas e contratos de API

## Estrutura
- `backend/` - API FastAPI e modelos de dominio
- `frontend/` - Frontend (Vite/React)
- `docs/` - Documentacao e engenharia reversa das telas
- `Infra/` - Infraestrutura (ex.: `docker-compose.yml`)

## Backend

### Requisitos
- Python 3.10+

### Setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Endpoint de saude: `GET /health`.

### Variaveis de ambiente
O backend carrega variaveis do `backend/.env` (copie de `backend/.env.example`).

Principais:
- `DATABASE_URL`: conexao usada pela API (Postgres/Supabase)
- `DIRECT_URL`: conexao direta para migrations/seed (no Supabase, recomendado para DDL/migrations)
- `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT
- `FRONTEND_ORIGIN`: CORS (ex.: `http://localhost:5173`)

Recuperacao de senha / email:
- `EMAIL_BACKEND=console|smtp`
- `PASSWORD_RESET_URL`, `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`, `PASSWORD_RESET_DEBUG`
- `SMTP_*` (quando `EMAIL_BACKEND=smtp`)

### Migrations e seed (dev)
```bash
cd backend
alembic upgrade head
python scripts/seed_sample.py
```

Notas:
- `seed_sample.py` cria agencias/diretorias e usuarios de exemplo (senha via `SEED_PASSWORD`, padrao `Senha123!`).
- Alembic no Supabase: prefira `DIRECT_URL` (porta 5432). O pooler (porta 6543) pode dar timeout em alguns ambientes.
- Se aparecer `Target database is not up to date`, rode `alembic upgrade head` antes do `alembic revision --autogenerate`.
- Se aparecer `Multiple head revisions`, use `alembic heads` e `alembic merge`.

## Frontend

### Requisitos
- Node.js 18+

### Setup
```bash
cd frontend
npm install
npm run dev
```

### Variaveis de ambiente
Por padrao o front usa `http://localhost:8000`. Para alterar:
```bash
cp .env.example .env
# edite VITE_API_BASE_URL
```

### Rotas principais
- Publicas: `/login`, `/novo-usuario`, `/reset-password`
- Protegidas: `/eventos`, `/eventos/novo`, `/eventos/:id`
- Auxiliar: `/success` (exibe JSON do usuario logado)

## Documentacao
- Autenticacao e recuperacao de senha (API): `docs/auth.md`
- Eventos (API): `docs/eventos_api.md`
- Login (UI): `docs/login/login.md`
- Cadastro de usuario (UI + API): `docs/login/new_user/login_tela_inicial.md`
- Eventos (UI): `docs/tela-inicial/menu/Eventos/eventos.md`

## Testes
```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -q

cd ../frontend
npm test -- --run
```

## Seguranca (importante)
Nao versione segredos em `.env`. Use `.env.example` como template e mantenha credenciais apenas localmente (ou via secrets do deploy).
