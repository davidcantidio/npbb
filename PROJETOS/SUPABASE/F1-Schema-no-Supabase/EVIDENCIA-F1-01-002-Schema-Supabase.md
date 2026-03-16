# Evidência F1-01-002 - Schema do Supabase validado com Alembic

**Issue:** ISSUE-F1-01-002 - Validar schema do Supabase com Alembic upgrade head  
**Data:** 2026-03-16  
**Status:** Concluído com sucesso

## Resumo

`alembic upgrade head` foi executado com sucesso contra o Supabase. O schema atual do repositório foi aplicado até o head e o histórico Alembic permanece coerente (head único).

## Premissas de ambiente

- `DIRECT_URL` e `DATABASE_URL` configuradas em `backend/.env`
- `backend/alembic/env.py` prioriza `DIRECT_URL` para migrations (contrato Supabase)
- Fallback para `DATABASE_URL` quando `DIRECT_URL` falha (run_migrations_online)

## Comandos executados

```bash
cd backend && alembic upgrade head
cd backend && alembic current
cd backend && alembic heads
cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py
```

## Resultado observado

| Verificação | Resultado |
|------------|-----------|
| `alembic upgrade head` | Concluído sem erro |
| Revision final (banco) | `a7b8c9d0e1f2` (head) |
| Head único no histórico | Confirmado |
| test_alembic_single_head.py | 1 passed |

## Bloqueios para F2

Nenhum. O schema do Supabase está alinhado ao head atual do repositório. A fase de migração de dados (F2) pode ser iniciada sobre um schema válido.

## Checklist mínimo para F2

- [x] Schema aplicado no Supabase via `alembic upgrade head` com `DIRECT_URL`
- [x] Histórico Alembic com head único preservado
- [x] Evidência técnica consolidada
