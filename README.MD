# NPBB - Sistema de gestão de eventos

Este repositório contém:
- **backend** em FastAPI/SQLModel (API + regras de negócio)
- **frontend** em Vite/React/MUI (login/cadastro e módulo Eventos)
- **docs** com especificações de telas e contratos de API

## Estrutura
- `backend/` - API FastAPI e modelos de domínio
- `frontend/` - Frontend (Vite/React)
- `docs/` - Documentação e engenharia reversa das telas
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

Endpoint de saúde: `GET /health`.

### Variáveis de ambiente
O backend carrega variáveis do `backend/.env` (copie de `backend/.env.example`).

Principais:
- `DATABASE_URL`: conexão usada pela API (Postgres/Supabase)
- `DIRECT_URL`: conexão direta para migrations/seed (no Supabase, recomendado para DDL/migrations)
- `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT
- `FRONTEND_ORIGIN`: CORS (ex.: `http://localhost:5173`)
- `PUBLIC_LANDING_BASE_URL`: base pública do backend para URLs de landing (ex.: `http://localhost:8000`)

Recuperação de senha / email:
- `EMAIL_BACKEND=console|smtp`
- `PASSWORD_RESET_URL`, `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`, `PASSWORD_RESET_DEBUG`
- `SMTP_*` (quando `EMAIL_BACKEND=smtp`)

### Migrations e seed (dev)
```bash
cd backend
alembic upgrade head
python scripts/seed_domains.py
python scripts/seed_sample.py
```

Notas:
- `seed_domains.py` popula apenas tabelas de domínio (diretorias/divisoes/tipos/subtipos/territorios/tags/status).
- `seed_sample.py` cria agências/diretorias e usuários de exemplo (senha via `SEED_PASSWORD`, padrão `Senha123!`).
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

### Variáveis de ambiente
Por padrão o front usa `http://localhost:8000`. Para alterar:
```bash
cp .env.example .env
# edite VITE_API_BASE_URL
```

### Rotas principais
- Públicas: `/login`, `/novo-usuário`, `/reset-password`
- Protegidas: `/eventos`, `/eventos/novo`, `/eventos/:id`
- Auxiliar: `/success` (exibe JSON do usuário logado)

## Documentação
- Autenticação e recuperação de senha (API): `docs/auth.md`
- Eventos (API): `docs/eventos_api.md`
- Formulário de Lead (API): `docs/formulario_lead_api.md`
- Gamificação (API): `docs/gamificacao_api.md`
- Ativações (API): `docs/ativacoes_api.md`
- Questionário (API): `docs/questionario_api.md`
- Login (UI): `docs/login/login.md`
- Cadastro de usuário (UI + API): `docs/login/new_user/login_tela_inicial.md`
- Eventos (UI): `docs/tela-inicial/menu/Eventos/eventos.md`

## Padrão de linguagem (pt-BR)
- Interfaces, mensagens e documentação devem usar Português do Brasil com acentuação correta.
- Exemplos: Saúde, Período, Diretoria, Divisão, Agência.

## Testes
```bash
# Backend (pytest)
cd backend
.\.venv\Scripts\python.exe -m pytest -q

# Frontend (vitest)
cd ../frontend
npm test -- --run

# E2E (Playwright) - requer backend + frontend rodando e seed aplicado
cd ../
npx playwright test
```

## Segurança (importante)
Não versione segredos em `.env`. Use `.env.example` como template e mantenha credenciais apenas localmente (ou via secrets do deploy).

## Mudanças recentes (Eventos)
- Layout: menu principal movido para o cabecalho; barra lateral reservada para filtros e funcionalidades da tela.
- Lista de eventos: coluna **Agência** substitui QRCode, com dropdown inline (mesmo comportamento da Diretoria).
- Padronização visual: Agência/Diretoria/Status/Investimento com mesma altura, borda e fonte do botão **Adicionar**.
- Período: linha do tempo centralizada com linha pontilhada e pontos diários; em andamento = verde, encerrado = azul.
- Saúde dos dados: ícone de estetoscópio (Font Awesome) + badge com cor do nível e texto com contraste.
- Configuração de score ajustada (agência e investimento valem mais). Arquivo: `docs/eventos_saúde_dados_config.json`
  **Importante:** reiniciar a API para aplicar (config  cacheada).

