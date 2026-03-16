---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-01-002-Validar-Scripts-Criticos-e-Invariantes-de-Teste"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T2 - Validar fallback SQLite quando TESTING=true

## objetivo

Provar explicitamente que o backend preserva o fallback de testes em SQLite.

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/db/database.py`
- `backend/tests/test_alembic_single_head.py`

## passos_atomicos

1. revisar a funcao de resolucao de URL em `backend/app/db/database.py`
2. executar uma validacao direta da resolucao com `TESTING=true`
3. executar a validacao automatizada minima existente do historico Alembic em contexto de testes
4. registrar o resultado como evidencia de que a migracao para Supabase nao removeu o isolamento dos testes

## comandos_permitidos

- `cd backend && PYTHONPATH=.. TESTING=true python -c "from app.db.database import _get_database_url; print(_get_database_url())"`
- `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`

## resultado_esperado

Fallback de testes resolvido para SQLite e validacao minima verde.

## testes_ou_validacoes_obrigatorias

- `cd backend && PYTHONPATH=.. TESTING=true python -c "from app.db.database import _get_database_url; print(_get_database_url())"`
- `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`

## stop_conditions

- parar se o fallback de testes deixar de apontar para SQLite ou se a validacao minima falhar
