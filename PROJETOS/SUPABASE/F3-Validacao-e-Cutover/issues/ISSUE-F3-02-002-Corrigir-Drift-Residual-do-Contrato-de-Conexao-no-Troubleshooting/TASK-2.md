---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-02-002-Corrigir-Drift-Residual-do-Contrato-de-Conexao-no-Troubleshooting"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T2 - Validar coerencia final entre env, setup e troubleshooting

## objetivo

Executar uma validacao final curta e repetivel para comprovar que o drift
documental local foi removido sem quebrar o fallback de testes.

## precondicoes

- T1 concluida
- `backend/app/db/database.py` disponivel para confronto com o fallback de testes

## arquivos_a_ler_ou_tocar

- `docs/TROUBLESHOOTING.md`
- `backend/.env.example`
- `docs/SETUP.md`
- `backend/app/db/database.py`

## passos_atomicos

1. comparar os trechos de `DATABASE_URL`, `DIRECT_URL`, Supabase e SQLite entre `docs/TROUBLESHOOTING.md`, `backend/.env.example` e `docs/SETUP.md`
2. confirmar que nenhum dos tres documentos volta a tratar `DATABASE_URL` e `DIRECT_URL` como equivalentes no runtime
3. rodar a validacao de fallback SQLite documentada para garantir que a correcao nao reintroduziu ambiguidade sobre testes
4. rodar o teste minimo de `test_alembic_single_head.py` citado no troubleshooting para preservar a evidencia objetiva ja usada na revisao
5. liberar a issue somente se a coerencia documental local e o fallback de testes permanecerem alinhados

## comandos_permitidos

- `rg -n "DATABASE_URL|DIRECT_URL|5432|6543|pooler|SQLite|TESTING" docs/TROUBLESHOOTING.md backend/.env.example docs/SETUP.md`
- `cd backend && PYTHONPATH=.. TESTING=true .venv/bin/python -c "from app.db.database import _get_database_url; print(_get_database_url())"`
- `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key .venv/bin/python -m pytest -q tests/test_alembic_single_head.py`

## resultado_esperado

Coerencia final confirmada entre os tres documentos locais e evidencias minimas
de fallback SQLite preservadas para a F3.

## testes_ou_validacoes_obrigatorias

- `rg -n "DATABASE_URL|DIRECT_URL|5432|6543|pooler|SQLite|TESTING" docs/TROUBLESHOOTING.md backend/.env.example docs/SETUP.md`
- `cd backend && PYTHONPATH=.. TESTING=true .venv/bin/python -c "from app.db.database import _get_database_url; print(_get_database_url())"`
- `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key .venv/bin/python -m pytest -q tests/test_alembic_single_head.py`

## stop_conditions

- parar se a validacao final mostrar nova contradicao material entre `docs/TROUBLESHOOTING.md`, `backend/.env.example` e `docs/SETUP.md`
- parar se o fallback SQLite deixar de retornar `sqlite:///./app.db`
- parar se o teste minimo falhar por regressao local ligada ao contrato de banco
