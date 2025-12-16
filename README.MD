NPBB — Sistema de gestão de eventos, ativações, leads e questionários
====================================================================

Este repositório reúne protótipos, backend em FastAPI e material de documentação do projeto NPBB.

Estrutura do repositório
------------------------
- backend/ — API FastAPI e modelos de domínio.
- frontend/ — código do front (Vite/React).
- docs/ — documentos e materiais de referência.
- Infra/ — arquivos de infraestrutura (ex.: docker-compose.yml).
- scripts/ — automações e scripts de suporte.

Requisitos
----------
- Python 3.10+ (backend)
- Node.js 18+ e npm (frontend)
- Docker opcional para orquestração local

Configuração de ambiente (.env)
-------------------------------
O backend carrega variáveis a partir de `backend/.env` (copie de `backend/.env.example`):
- `DATABASE_URL`: conexão usada pelo app (Postgres/Supabase).
- `DIRECT_URL`: conexão direta para migrations/seed (recomendado no Supabase).
- `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT.
- `FRONTEND_ORIGIN`: CORS liberado para o front (ex.: `http://localhost:5173`).

Observações:
- Em produção/homologação, o backend exige `DATABASE_URL` válido (fallback SQLite é apenas para testes com `TESTING=true` ou `pytest`).
- Em alguns ambientes o pooler do Supabase pode dar timeout; prefira `DIRECT_URL` (porta 5432) para migrations/DDL.

Backend: como rodar
-------------------
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Endpoint de saúde: `GET /health` (retorna `{"status": "ok"}`).

Migrations e seed (dev)
----------------------
```bash
cd backend
alembic upgrade head
python scripts/seed_sample.py
```
- O seed cria agências/diretorias e alguns usuários de exemplo. Para definir a senha usada, exporte `SEED_PASSWORD` (padrão: `Senha123!`).
- Para criar um admin via env vars: defina `ADMIN_EMAIL` e `ADMIN_PASSWORD` e rode `python scripts/seed_admin.py`.
- Para criar uma migration: rode `alembic upgrade head`, depois `alembic revision --autogenerate -m "sua-mensagem"` e por fim `alembic upgrade head`.
- Dicas: `Target database is not up to date` -> rode `alembic upgrade head` antes do autogenerate; `Multiple head revisions` -> use `alembic heads` e `alembic merge`.

Frontend: como rodar
--------------------
```bash
cd frontend
npm install
npm run dev
```
O Vite exibirá a URL local no terminal (geralmente http://localhost:5173).

Frontend: variáveis de ambiente
------------------------------
Por padrão o front usa a API em `http://localhost:8000`. Para alterar, copie `frontend/.env.example` para `frontend/.env` e ajuste:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

Rotas principais
----------------
- `/login` (pública)
- `/novo-usuario` (pública)
- `/reset-password` (pública, usado no link de recuperação)
- `/` (protegida, exige login)
- `/success` (protegida, exibe JSON do usuário logado)

Recuperacao de senha: na tela de login ha o link "Esqueceu a senha?" que chama `POST /usuarios/forgot-password`; o link abre `/reset-password?token=...` e consome `POST /usuarios/reset-password` (detalhes em `docs/auth.md`).

Docker (opcional)
-----------------
```bash
docker compose up --build
```
Ajuste portas/variáveis no `Infra/docker-compose.yml` conforme necessário.

Documentação
------------
Materiais de apoio e notas estão em `docs/`.
- `docs/auth.md`: contrato dos endpoints `/auth/login` e `/auth/me`.
- `docs/login/new_user/login_tela_inicial.md`: especificação/fluxo do cadastro (`GET /agencias/`, `POST /usuarios/`).
