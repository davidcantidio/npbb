---
doc_id: "EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md"
version: "1.0"
status: "done"
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
- [x] fluxo de migrations alinhado ao contrato `DIRECT_URL` primeiro, `DATABASE_URL` como fallback
- [x] execucao de `alembic upgrade head` validada no Supabase
- [x] evidencia tecnica consolidada para liberar a fase de dados

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Adequar execucao de migrations ao Supabase | Alinhar entrypoints, fallback e mensagens de erro do fluxo Alembic | 3 | done | [ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md](./issues/ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md) |
| ISSUE-F1-01-003 | Endurecer fallback de URLs no fluxo Alembic | Corrigir o fallback do Alembic e cobrir o contrato de URLs com testes de regressao | 3 | done | [ISSUE-F1-01-003-Endurecer-Fallback-de-URLs-no-Fluxo-Alembic.md](./issues/ISSUE-F1-01-003-Endurecer-Fallback-de-URLs-no-Fluxo-Alembic.md) |
| ISSUE-F1-01-002 | Validar schema do Supabase com Alembic upgrade head | Executar e comprovar a subida do schema ate o head no ambiente alvo | 5 | done | [ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md](./issues/ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md) |
| ISSUE-F1-01-004 | Revalidar upgrade head no Supabase com evidencia rastreavel | Reexecutar a validacao no Supabase com prova objetiva do uso de `DIRECT_URL` e da revision final aplicada | 3 | done | [ISSUE-F1-01-004-Revalidar-Upgrade-Head-no-Supabase-com-Evidencia-Rastreavel.md](./issues/ISSUE-F1-01-004-Revalidar-Upgrade-Head-no-Supabase-com-Evidencia-Rastreavel.md) |
| ISSUE-F1-01-005 | Endurecer revalidacao head no Supabase sem fallback ambiguo | Modo estrito ALEMBIC_STRICT_DIRECT_URL que aceite apenas DIRECT_URL e gere evidencia bruta para liberar F2 | 3 | done | [ISSUE-F1-01-005-Endurecer-Revalidacao-Head-no-Supabase-sem-Fallback-Ambiguo.md](./issues/ISSUE-F1-01-005-Endurecer-Revalidacao-Head-no-Supabase-sem-Fallback-Ambiguo.md) |
| ISSUE-F1-01-006 | Fechar cobertura do modo estrito e alinhar gate da fase | Fechar lacuna de regressao do modo estrito e alinhar estado documental do gate | 2 | done | [ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md](./issues/ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md) |
| ISSUE-F1-01-007 | Sincronizar cascata documental do fechamento da F1 | Corrigir a cascata documental local apos a review da ISSUE-F1-01-006 | 1 | done | [ISSUE-F1-01-007-Sincronizar-Cascata-Documental-do-Fechamento-da-F1](./issues/ISSUE-F1-01-007-Sincronizar-Cascata-Documental-do-Fechamento-da-F1/) |
| ISSUE-F1-01-008 | Commit e revalidar auditoria F1 | Fazer commit dos artefatos e revalidar auditoria com arvore limpa (follow-up B1 F1-R01) | 1 | done | [ISSUE-F1-01-008-Commit-e-Revalidar-Auditoria-F1](./issues/ISSUE-F1-01-008-Commit-e-Revalidar-Auditoria-F1/) |

## Artifact Minimo do Epico

- fluxo de migrations coerente com o contrato do Supabase
- evidencia de execucao de `alembic upgrade head` ate o head atual
- validacao minima do historico Alembic preservada

## Dependencias
- [Intake](../INTAKE-SUPABASE.md)
- [PRD](../PRD-SUPABASE.md)
- [Fase](./F1_SUPABASE_EPICS.md)
