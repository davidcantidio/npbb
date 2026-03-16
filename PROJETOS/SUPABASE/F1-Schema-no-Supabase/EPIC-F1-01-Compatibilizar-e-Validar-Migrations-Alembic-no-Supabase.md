---
doc_id: "EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# EPIC-F1-01 - Compatibilizar e validar migrations Alembic no Supabase

## Objetivo

Compatibilizar os entrypoints e o contrato de configuracao de migrations com o
uso de `DIRECT_URL` no Supabase e, em seguida, validar que o schema atual sobe
ate o head sem erro no ambiente alvo.

## Resultado de Negocio Mensuravel

- o schema do Supabase alcanca o mesmo head do ambiente local via `alembic upgrade head`
- o fluxo de migrations fica coerente com `DIRECT_URL` para DDL e `DATABASE_URL` como fallback
- a fase F2 inicia sobre um schema confiavel no Supabase

## Contexto Arquitetural

- `backend/alembic/env.py` ja prioriza `DIRECT_URL`, mas o fluxo de execucao ainda precisa ser consolidado nos wrappers e na validacao operacional
- `backend/scripts/migrate.ps1` ainda considera apenas `DATABASE_URL`, o que pode gerar divergencia com o contrato do Supabase
- `backend/tests/test_alembic_single_head.py` e a verificacao automatizada minima ja existente para o historico Alembic
- `backend/.env.example` e o principal ponto de referencia para as URLs de runtime e migrations

## Definition of Done do Epico
- [ ] fluxo de migrations alinhado ao contrato `DIRECT_URL` primeiro, `DATABASE_URL` como fallback
- [ ] execucao de `alembic upgrade head` validada no Supabase
- [ ] evidencia tecnica consolidada para liberar a fase de dados

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Adequar execucao de migrations ao Supabase | Alinhar entrypoints, fallback e mensagens de erro do fluxo Alembic | 3 | done | [ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md](./issues/ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md) |
| ISSUE-F1-01-002 | Validar schema do Supabase com Alembic upgrade head | Executar e comprovar a subida do schema ate o head no ambiente alvo | 5 | todo | [ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md](./issues/ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md) |

## Artifact Minimo do Epico

- fluxo de migrations coerente com o contrato do Supabase
- evidencia de execucao de `alembic upgrade head` ate o head atual
- validacao minima do historico Alembic preservada

## Dependencias
- [Intake](../INTAKE-SUPABASE.md)
- [PRD](../PRD-SUPABASE.md)
- [Fase](./F1_SUPABASE_EPICS.md)
