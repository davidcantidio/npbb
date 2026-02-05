# Arquitetura (visao rapida)

## Backend (FastAPI + SQLModel)
Estrutura principal em `backend/app`:
- `core/`: auth, dependencias e regras centrais.
- `db/`: configuracao de engine/sessao + metadata.
- `models/`: modelos SQLModel (schema do banco).
- `schemas/`: contratos Pydantic.
- `routers/`: endpoints FastAPI.
- `services/`: regras de negocio e agregacoes.
- `utils/`: funcoes auxiliares (normalizacao, log sanitize, etc).

Migrations:
- Alembic em `backend/alembic/` (fonte oficial).

## Frontend (Vite + React + MUI)
Estrutura principal em `frontend/src`:
- `components/`: layout e UI comum.
- `pages/`: telas (ex.: Leads, Dashboard Leads).
- `services/`: clientes de API.
- `store/`: auth/token (se aplicavel).

## Banco de dados
- Postgres (Supabase).
- Conexao via `DATABASE_URL` (runtime) e `DIRECT_URL` (migrations).
- Recomendacao: manter **dados agregados** nas rotas de dashboard (sem PII).

## Integracoes
- Email (console ou SMTP).
- Export DOCX (python-docx) via script.

## Decisoes importantes
- Importacao de leads via CSV/XLSX com mapeamento assistido.
- Dashboard e relatorios retornam **apenas agregados** (sem email/cpf/telefone).

