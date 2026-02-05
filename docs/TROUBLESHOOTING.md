# Troubleshooting

## 1) DATABASE_URL nao configurada
**Sintoma:** `RuntimeError: DATABASE_URL nao configurada ...`
**Solucao:** crie `backend/.env` a partir de `.env.example` e configure `DATABASE_URL`.

## 2) Uvicorn nao encontrado
**Sintoma:** `No module named uvicorn`
**Solucao:** ative a venv e rode `pip install -r requirements.txt`.

## 3) Falha no import XLSX (openpyxl)
**Sintoma:** `ModuleNotFoundError: openpyxl`
**Solucao:** confirme `openpyxl` em `requirements.txt` e rode `pip install -r requirements.txt`.

## 4) Upload nao funciona (python-multipart)
**Sintoma:** `RuntimeError: Form data requires "python-multipart"`
**Solucao:** confirme `python-multipart` em `requirements.txt` e reinstale deps.

## 5) Vite falha com "@vitejs/plugin-react"
**Sintoma:** `Cannot find package '@vitejs/plugin-react'`
**Solucao:** rode `npm install` no `frontend/`.

## 6) Erro "Unexpected <<<<<<<" no front
**Sintoma:** arquivo com marcadores de conflito.
**Solucao:** resolva o merge no arquivo indicado (ex.: `frontend/src/main.tsx`).

## 7) node_modules nao remove (Permission denied)
**Sintoma:** `Permission denied` ao deletar `node_modules/`.
**Solucao:** feche editores/servidores rodando e tente novamente:
```bash
Remove-Item -Recurse -Force frontend/node_modules
```

## 8) Alembic "Target database is not up to date"
**Solucao:** rode `alembic upgrade head` antes do autogenerate.

## 9) Vite CORS / API nao responde
**Sintoma:** erro 401/403 ou CORS.
**Solucao:** ajuste `FRONTEND_ORIGIN` no backend e `VITE_API_BASE_URL` no front.

## 10) PydanticSerializationUnexpectedValue (data_health)
**Sintoma:** warning do Pydantic ao serializar.
**Solucao:** garantir que `data_health` e um objeto do schema (ver `eventos.py`).

## 11) Supabase: pooler vs conexao direta
**Sintoma:** timeouts ou erro de migrations.
**Solucao:** use `DIRECT_URL` (porta 5432) para migrations/seed e `DATABASE_URL` (pooler) para runtime.

## 12) Tests falham por SQLite
**Sintoma:** erro de conexao no pytest.
**Solucao:** exporte `TESTING=true` ou configure `DATABASE_URL` para um banco de teste.

