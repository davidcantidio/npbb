# Evidência F1-01-005 - Revalidação head no Supabase sem fallback ambíguo

**Issue:** ISSUE-F1-01-005 - Endurecer revalidacao head no Supabase sem fallback ambiguo  
**Data:** 2026-03-16  
**Status:** Concluído com sucesso

## Resumo

Revalidação executada com sucesso em **modo estrito** (`ALEMBIC_STRICT_DIRECT_URL=true`). O modo estrito garante por construção que apenas `DIRECT_URL` foi usada — sem possibilidade de fallback silencioso para `DATABASE_URL`. O ambiente alvo está na revision `a7b8c9d0e1f2` (head) e o histórico Alembic permanece com head único.

## Modo estrito

- **Flag:** `ALEMBIC_STRICT_DIRECT_URL=true`
- **Comportamento:** `get_urls()` retorna somente `DIRECT_URL`; falha cedo se ausente
- **Prova:** Sucesso da rodada prova objetivamente que a conexão direta foi a rota usada (sem inferência)

## Comandos executados

```bash
cd backend && ALEMBIC_STRICT_DIRECT_URL=true python3 -m alembic upgrade head
cd backend && ALEMBIC_STRICT_DIRECT_URL=true python3 -m alembic current
cd backend && TESTING=true python3 -m alembic heads
cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py
```

## Saída observada

### alembic upgrade head (modo estrito)

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### alembic current (modo estrito)

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
a7b8c9d0e1f2 (head)
```

### alembic heads

```
a7b8c9d0e1f2 (head)
```

### test_alembic_single_head.py

```
1 passed in 0.06s
```

## Resultado consolidado

| Verificação | Resultado |
|------------|-----------|
| `alembic upgrade head` (modo estrito) | Concluído sem erro |
| Uso exclusivo de `DIRECT_URL` | Garantido por construção (modo estrito) |
| Revision final (banco) | `a7b8c9d0e1f2` (head) |
| `alembic current` (modo estrito) | `a7b8c9d0e1f2 (head)` |
| Head único no histórico | Confirmado |
| test_alembic_single_head.py | 1 passed |

## Prontidão para F2

**Liberada.** O schema do Supabase está comprovadamente alinhado ao head atual do repositório. A revalidação usou exclusivamente `DIRECT_URL` (modo estrito), sem ambiguidade sobre a rota efetivamente utilizada. A fase de migração de dados (F2) pode ser iniciada sobre um schema válido.

## Checklist mínimo para F2

- [x] Rodada real de `alembic upgrade head` executada no Supabase com modo estrito
- [x] Modo estrito garante uso exclusivo de `DIRECT_URL` (sem fallback)
- [x] Saída observada de `alembic upgrade head` e `alembic current` registrada
- [x] Revision final `a7b8c9d0e1f2 (head)` confirmada
- [x] Verificação automatizada de head único reexecutada com sucesso
- [x] Status de prontidão para F2 declarado sem inferência
