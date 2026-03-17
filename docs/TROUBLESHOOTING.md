# Troubleshooting

Banco padrao do projeto: Supabase. PostgreSQL local e opcional (dev) ou usado apenas em scripts de migracao F2.

## 1) DATABASE_URL nao configurada
**Sintoma:** `RuntimeError: DATABASE_URL nao configurada ...`
**Solucao:** crie `backend/.env` a partir de `.env.example` e configure `DATABASE_URL`/`DIRECT_URL`.

Para Supabase: use `postgresql+psycopg2://` (nao `postgresql://`). Senhas com `@` ou `&` precisam ser URL-encoded (`@` -> `%40`, `&` -> `%26`). No contrato atual da F3, `DATABASE_URL` e a conexao de runtime da API e `DIRECT_URL` fica reservada a migrations/seed. Exemplo:
```
DATABASE_URL=postgresql+psycopg2://postgres.PROJECT_REF:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
DIRECT_URL=postgresql+psycopg2://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
```
Nao reutilize a URL direta (`:5432`) como `DATABASE_URL` no runtime do backend. Obtenha as strings em Supabase Dashboard > Settings > Database > Connection string.

## 2) Uvicorn nao encontrado
**Sintoma:** `No module named uvicorn`
**Solucao:** recrie/ative a venv com Python 3.12 e reinstale deps:
```bash
cd backend
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 3) `ModuleNotFoundError: No module named 'app'`
**Sintoma:** erro ao rodar `uvicorn app.main:app --reload` na raiz do repo.
**Solucao:** use o launcher oficial da raiz:
```bash
source backend/.venv/bin/activate
./scripts/dev_backend.sh
```

Alternativa tecnica:
```bash
source backend/.venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --reload --app-dir backend
```

## 4) `ModuleNotFoundError: No module named 'core'`
**Sintoma:** backend falha ao importar `from core...`.
**Solucao:** suba a API com `PYTHONPATH=..` ou use o launcher:
```bash
cd backend
./scripts/dev_api.sh
```

## 5) Falha no import XLSX (openpyxl)
**Sintoma:** `ModuleNotFoundError: openpyxl`
**Solucao:** confirme `openpyxl` em `requirements.txt` e rode `pip install -r requirements.txt`.

## 6) Upload nao funciona (python-multipart)
**Sintoma:** `RuntimeError: Form data requires "python-multipart"`
**Solucao:** confirme `python-multipart` em `requirements.txt` e reinstale deps.

## 7) Vite falha com "@vitejs/plugin-react"
**Sintoma:** `Cannot find package '@vitejs/plugin-react'`
**Solucao:** rode `npm install` no `frontend/`.

## 8) Erro "Unexpected <<<<<<<" no front
**Sintoma:** arquivo com marcadores de conflito.
**Solucao:** resolva o merge no arquivo indicado (ex.: `frontend/src/main.tsx`).

## 9) node_modules nao remove (Permission denied)
**Sintoma:** `Permission denied` ao deletar `node_modules/`.
**Solucao:** feche editores/servidores rodando e tente novamente:
```bash
Remove-Item -Recurse -Force frontend/node_modules
```

## 10) Alembic "Target database is not up to date"
**Solucao:** rode `alembic upgrade head` antes do autogenerate.

## 11) Vite CORS / API nao responde
**Sintoma:** erro 401/403 ou CORS.
**Solucao:**
- Em dev local, use `VITE_API_BASE_URL=/api` (ou deixe sem definir para usar `/api` por padrao).
- Garanta backend em `http://localhost:8000` e frontend em `http://localhost:5173`.
- O Vite faz proxy de `/api/*` para `http://localhost:8000/*`.
- No backend, ajuste `FRONTEND_ORIGIN` para liberar a origem do frontend.

## 12) PydanticSerializationUnexpectedValue (data_health)
**Sintoma:** warning do Pydantic ao serializar.
**Solucao:** garantir que `data_health` e um objeto do schema (ver `eventos.py`).

## 13) Supabase: pooler vs conexao direta
**Sintoma:** timeouts ou erro de migrations.
**Solucao:** no Supabase, use `DIRECT_URL` (porta 5432) para migrations/seed e `DATABASE_URL` (pooler, tipicamente `:6543`) para runtime da API.

## 14) Tests falham por conexao no pytest
**Sintoma:** erro de conexao no pytest.
**Solucao:** exporte `TESTING=true` para usar SQLite automaticamente (caminho padrao de testes). Alternativa: configure `DATABASE_URL` para um banco de teste.

## 15) Validar runtime com Supabase
**Objetivo:** confirmar que o backend usa o Supabase como banco (nao PostgreSQL local).
**Passos:**
1. Configure `DATABASE_URL` com a URL de runtime da API no Supabase (pooler) e `DIRECT_URL` com a conexao direta reservada a migrations/seed.
2. Inicie o backend: `./scripts/dev_backend.sh` (a partir da raiz do repo).
3. Valide: `curl -sf http://127.0.0.1:8000/health` deve retornar `{"status":"ok"}`.
4. Valide endpoint com banco: `curl -sf http://127.0.0.1:8000/eventos/1/landing` deve retornar JSON com dados do evento.
Se `DATABASE_URL` apontar para `127.0.0.1`, `localhost` ou para a URL direta `:5432` do Supabase, o contrato operacional da F3 fica incorreto para o runtime.

## 16) backup_export_migracao falha (credenciais ou tooling)
**Contexto:** script de migracao F2 (backup Supabase + export local). PostgreSQL local nao e requisito para operacao normal.
**Sintoma:** `ERRO: LOCAL_DIRECT_URL nao configurado`, `pg_dump nao encontrado no PATH` ou `pg_restore nao encontrado no PATH`.
**Solucao:**
- Configure no `backend/.env`: `SUPABASE_DIRECT_URL` (ou `DIRECT_URL`) e `LOCAL_DIRECT_URL` (ver `.env.example`).
- Instale o cliente PostgreSQL (`brew install postgresql@16`) e garanta que `pg_dump` e `pg_restore` estejam no PATH.
- O script valida os dumps gerados com `pg_restore --list` antes de declarar prontidao; nao executa nenhum passo destrutivo no Supabase.

## 17) validacao_pos_carga_migracao falha
**Sintoma:** `ERRO: Artefato backup_supabase nao encontrado`, `ERRO: DATABASE_URL aponta para alvo diferente...` ou falha ao consultar tabelas do Supabase.
**Solucao:**
- Gere ou regenere os dumps mais recentes com `cd backend && python -m scripts.backup_export_migracao`.
- Confirme que `SUPABASE_DIRECT_URL` (ou `DIRECT_URL`) e `DATABASE_URL` apontam para o mesmo projeto Supabase; runtime remoto diferente nao e aceito.
- Confirme `pg_restore` no PATH; o script usa `pg_restore --list` e `pg_restore --help` para validar a viabilidade do rollback.
- Se a falha apontar tabela ausente ou inacessivel, nao libere F3; revise a recarga e preserve o backup para rollback.

## 18) Checklist pos-cutover: scripts criticos e fallback de testes
**Objetivo:** evidencias minimas de coerencia entre operacao (Supabase) e testes (SQLite) apos F3.
**Scripts criticos:** `seed_common.py` prefere `DIRECT_URL`; `seed_domains.py` usa `get_engine_for_scripts`; `seed_sample.py` prefere `DIRECT_URL` depois `DATABASE_URL`. Nenhum assume PostgreSQL local como padrao.
**Fallback de testes:** com `TESTING=true`, `database.py` retorna `sqlite:///./app.db` (sem `DATABASE_URL_TEST` ou `FORCE_DATABASE_URL_IN_TESTS`).
**Validacao:** `cd backend && PYTHONPATH=.. TESTING=true .venv/bin/python -c "from app.db.database import _get_database_url; print(_get_database_url())"` deve imprimir `sqlite:///./app.db`.
**Teste minimo:** `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key .venv/bin/python -m pytest -q tests/test_alembic_single_head.py` deve passar.
