# Setup (Backend + Frontend)

Este guia cobre o setup completo. Se quiser apenas o caminho feliz, veja o README.

## TL;DR (caminho feliz)
```bash
# backend (raiz do repo) — Supabase como banco unico
cd backend
/opt/homebrew/bin/python3.12 -m venv .venv  # macOS/Homebrew
# python -m venv .venv  # Linux/Windows
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env  # configure DATABASE_URL e DIRECT_URL com seu projeto Supabase
cd ..
source backend/.venv/bin/activate
./scripts/dev_backend.sh

# frontend (em outro terminal)
cd frontend
npm install
# opcional: copy .env.example .env
npm run dev
```

## Pre-requisitos
- Python **3.12**
- Node.js **18+**
- Projeto Supabase (banco unico do projeto). PostgreSQL local e opcional para dev.

## Backend
### 0) Alternativa: PostgreSQL local (dev)
Se preferir rodar com banco local em vez do Supabase:
```bash
brew install postgresql@16
brew services start postgresql@16
/opt/homebrew/opt/postgresql@16/bin/createdb npbb  # execute uma vez (ignore se ja existir)
```

### 1) Criar ambiente virtual e instalar deps
```bash
cd backend
/opt/homebrew/bin/python3.12 -m venv .venv  # macOS/Homebrew
# python -m venv .venv  # Linux/Windows
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Observacao: O pacote `qrcode` (em requirements.txt) e necessario para gerar QR codes reais nas landing pages. Se aparecer um placeholder amarelo em vez de QR escaneavel, execute `pip install -r requirements.txt` para garantir que todas as dependencias estejam instaladas.

### 2) Variaveis de ambiente
Crie o arquivo `.env`:
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
```

Exemplo Supabase (substitua pelos seus valores do projeto):
```env
DATABASE_URL="postgresql+psycopg2://postgres.<project_ref>:<password>@<pooler_host>:6543/postgres"
DIRECT_URL="postgresql+psycopg2://postgres.<project_ref>:<password>@<db_host>:5432/postgres"
SECRET_KEY="change-me"
FRONTEND_ORIGIN="http://localhost:5173"
EMAIL_BACKEND="console"
PASSWORD_RESET_DEBUG="false"
DB_CONNECT_TIMEOUT=5
DB_POOL_TIMEOUT=5
DB_STATEMENT_TIMEOUT_MS=15000
LEAD_GOLD_STATEMENT_TIMEOUT_MS=600000
LEAD_GOLD_PROGRESS_HEARTBEAT_SECONDS=20
LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE_SUPABASE_POOLER_6543=25
LEAD_GOLD_INSERT_MAX_TRANSACTION_SECONDS_SUPABASE_POOLER_6543=15
```

Alternativa (PostgreSQL local para dev):
```env
DATABASE_URL="postgresql+psycopg2://seu_usuario_sistema@127.0.0.1:5432/npbb"
DIRECT_URL="postgresql+psycopg2://seu_usuario_sistema@127.0.0.1:5432/npbb"
```

Observacoes:
- `DATABASE_URL` e a conexao usada pela API.
- `DIRECT_URL` e a conexao direta para migrations/seed.
- `DB_CONNECT_TIMEOUT` deve ser menor que o timeout HTTP do frontend para a API retornar `503` estruturado quando o banco remoto estiver indisponivel, em vez de deixar o proxy do Vite abortar a conexao.
- `DB_POOL_TIMEOUT` e `DB_CONNECT_TIMEOUT` continuam sendo limites de infraestrutura/pool; nao use esses valores para acomodar processamento longo do pipeline Gold.
- `LEAD_GOLD_STATEMENT_TIMEOUT_MS` controla o limite por statement/transacao de cada chunk de persistencia do Gold; ele nao representa o tempo total permitido para a execucao inteira do pipeline.
- `LEAD_GOLD_PROGRESS_HEARTBEAT_SECONDS` atualiza `pipeline_progress.updated_at` durante chunks lentos do Gold para evitar falso alerta de stall na UI sem mascarar falhas reais de banco ou rede.
- Se `DATABASE_URL` usar o pooler transacional compartilhado do Supabase (`:6543`), o Gold aplica um cap efetivo de chunk por linhas (`LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE_SUPABASE_POOLER_6543`) e um budget de tempo por transacao aberta (`LEAD_GOLD_INSERT_MAX_TRANSACTION_SECONDS_SUPABASE_POOLER_6543`) para reduzir pressao no pooler e evitar transacoes muito longas no plano Free.
- O backend aceita variaveis separadas (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`) como fallback.
- Em testes, o backend permite SQLite se `TESTING=true` ou `PYTEST_CURRENT_TEST` estiver setado.
- Para startup local, rode com `PYTHONPATH=..` (ou use `./scripts/dev_api.sh`) porque o backend importa o pacote compartilhado `core/`.

### 2.1) URL publica do app no go-live
O backend resolve a URL publica do app na mesma ordem implementada em
`backend/app/utils/urls.py`:

1. `PUBLIC_APP_BASE_URL`
2. primeiro origin de `FRONTEND_ORIGIN`
3. fallback de desenvolvimento: `http://localhost:5173`

Regras de uso:
- Em desenvolvimento local, o fallback `http://localhost:5173` e aceitavel.
- Em producao, `PUBLIC_APP_BASE_URL` e obrigatoria.
- Para o go-live deste projeto, o valor canonico esperado e `https://app.npbb.com.br`.
- `FRONTEND_ORIGIN` pode continuar configurado, mas nao deve ser tratado como fonte
  confiavel para o host publico final do go-live.

Risco operacional:
- Se `PUBLIC_APP_BASE_URL` nao estiver configurada em producao, o sistema pode
  persistir links publicos e QR codes com host incorreto, incluindo `localhost`
  ou um dominio provisorio, comprometendo o acesso da landing publica.

### 3) Rodar a API
Opcao A (raiz do repo, oficial):
```bash
source backend/.venv/bin/activate
./scripts/dev_backend.sh
```

Windows/PowerShell:
```powershell
.\scripts\dev_backend.ps1
```

Opcao B (dentro de `backend/`, oficial):
```bash
PYTHONPATH=.. python -m uvicorn app.main:app --reload
# alternativa:
./scripts/dev_api.sh
```

Opcao tecnica alternativa (raiz):
```bash
source backend/.venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --reload --app-dir backend
```

Importante:
- `uvicorn app.main:app --reload` na raiz, sem `PYTHONPATH` e sem `--app-dir backend`, nao e suportado.
- Se `Get-NetTCPConnection -LocalPort 8000` mostrar `Python312\python.exe` global em vez de `backend\.venv\Scripts\python.exe`, encerre esse processo e suba pelo script oficial.
- Antes de iniciar fluxos do frontend que fazem polling, valide `http://127.0.0.1:8000/health` e `http://127.0.0.1:8000/health/ready`.

### 4) Migrations (dev)
```bash
alembic upgrade head
```

### 5) Seeds (opcional)
```bash
python scripts/seed_domains.py
python scripts/seed_sample.py
```

### 6) Migracao F2 (backup e export)
Para gerar backup do Supabase e export do PostgreSQL local antes da recarga:
```bash
cd backend && python -m scripts.backup_export_migracao
```
Configure `SUPABASE_DIRECT_URL` (ou `DIRECT_URL`) e `LOCAL_DIRECT_URL` no `.env`. O script exige `pg_dump` e `pg_restore` no PATH (o segundo é usado para validar os dumps antes de declarar sucesso). Ver [RUNBOOK-MIGRACAO-SUPABASE.md](RUNBOOK-MIGRACAO-SUPABASE.md).

### 7) Migracao F2 (validacao pos-carga)
Depois da recarga no Supabase, execute o checklist nao destrutivo da F2-02-002:
```bash
cd backend && python -m scripts.validacao_pos_carga_migracao
```
Configure `DATABASE_URL` e `DIRECT_URL`/`SUPABASE_DIRECT_URL` para o mesmo projeto Supabase. O script exige `pg_restore` no PATH, reutiliza os dumps mais recentes em `artifacts_migracao/` e bloqueia a liberacao para F3 quando backup/export estiverem ilegiveis, quando runtime e manutencao divergirem ou quando as tabelas exportadas nao existirem no alvo recarregado.

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

Exemplo (alinhe com `frontend/.env.example`):
```env
VITE_API_BASE_URL=/api
VITE_SPONSORSHIP_USE_API=true
```

Observacao:
- Em dev local, o Vite faz proxy de `/api/*` para `http://localhost:8000/*` (com rewrite de prefixo).  
- Se `VITE_API_BASE_URL` nao for definido, o frontend usa `/api` por padrao.
- Patrocinados exige `VITE_SPONSORSHIP_USE_API=true` (sem isso, a UI mostra aviso e nao usa a API `/sponsorship`).

### 3) Rodar o front
```bash
npm run dev
```

Observacao:
- O frontend em desenvolvimento tambem pode ser acessado de outro dispositivo na mesma rede por `http://<IPv4>:5173`.
- No Windows, descubra o IP local com `ipconfig`.
- O proxy `/api` continua apontando para o backend local da maquina que esta rodando o Vite.

## Comandos rapidos
- Backend (raiz): `./scripts/dev_backend.sh`
- Backend (pasta backend): `PYTHONPATH=.. python -m uvicorn app.main:app --reload` (ou `./scripts/dev_api.sh`)
- Tests (backend): `python -m pytest -q`
- Tests (frontend): `npm test -- --run`
- E2E browser install (frontend): `cd frontend && npx playwright install chromium`
- E2E listagem (frontend): `cd frontend && npx playwright test --list`
- E2E suite (frontend): `cd frontend && npm run test:e2e`
- E2E CPF-first (frontend): `cd frontend && npx playwright test issue-f2-01-003-cpf-first.spec.ts`
- Lint (frontend): `npm run lint`
- Typecheck (frontend): `npm run typecheck`

## TODO (nao encontrado no repo)
- Ambiente docker-compose para subir tudo localmente.
