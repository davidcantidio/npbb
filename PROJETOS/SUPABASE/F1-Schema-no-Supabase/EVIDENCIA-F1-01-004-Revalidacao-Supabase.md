# Evidência F1-01-004 - Revalidação upgrade head no Supabase com evidência rastreável

**Issue:** ISSUE-F1-01-004 - Revalidar upgrade head no Supabase com evidencia rastreavel  
**Data:** 2026-03-16  
**Status:** Concluído com sucesso

## Resumo

Revalidação executada com sucesso. O comando `alembic upgrade head` foi executado contra o Supabase com prova objetiva do uso de `DIRECT_URL`. O ambiente alvo está na revision `a7b8c9d0e1f2` (head) e o histórico Alembic permanece com head único.

## Premissas de ambiente

- `DIRECT_URL` e `DATABASE_URL` configuradas em `backend/.env` ou passadas explicitamente na invocação
- `backend/alembic/env.py` prioriza `DIRECT_URL` para migrations (contrato Supabase)
- Procedimento canônico: invocar com `DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL"` para evidência explícita

## Comandos executados

```bash
cd backend && DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL" alembic upgrade head
cd backend && DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL" alembic current
cd backend && TESTING=true python3 -m alembic heads
cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py
```

## Resultado observado

| Verificação | Resultado |
|------------|-----------|
| `alembic upgrade head` | Concluído sem erro |
| Uso de `DIRECT_URL` | Confirmado (comando explícito e env.py prioriza DIRECT_URL) |
| Revision final (banco) | `a7b8c9d0e1f2` (head) |
| `alembic current` | `a7b8c9d0e1f2 (head)` |
| Head único no histórico | Confirmado |
| test_alembic_single_head.py | 1 passed |

## Bloqueios para F2

Nenhum. O schema do Supabase está comprovadamente alinhado ao head atual do repositório via conexão direta (`DIRECT_URL`). A fase de migração de dados (F2) pode ser iniciada sobre um schema válido.

## Checklist mínimo para F2

- [x] Rodada real de `alembic upgrade head` executada no Supabase com `DIRECT_URL`
- [x] Revision final observada no ambiente alvo registrada com evidência mínima
- [x] Verificação automatizada de head único reexecutada com sucesso
- [x] Status de prontidão para F2 declarado sem inferência
