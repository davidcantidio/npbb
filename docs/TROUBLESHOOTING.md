# Troubleshooting

## 1) DATABASE_URL nao configurada
**Sintoma:** `RuntimeError: DATABASE_URL nao configurada ...`
**Solucao:** crie `backend/.env` a partir de `.env.example` e configure `DATABASE_URL`/`DIRECT_URL` (ex.: `postgresql+psycopg2://seu_usuario_sistema@127.0.0.1:5432/npbb`).

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
**Solucao:** use `DIRECT_URL` (porta 5432) para migrations/seed e `DATABASE_URL` (pooler) para runtime.

## 14) Tests falham por SQLite
**Sintoma:** erro de conexao no pytest.
**Solucao:** exporte `TESTING=true` ou configure `DATABASE_URL` para um banco de teste.
