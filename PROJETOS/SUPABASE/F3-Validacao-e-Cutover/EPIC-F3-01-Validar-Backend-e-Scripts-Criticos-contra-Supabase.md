---
doc_id: "EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# EPIC-F3-01 - Validar backend e scripts criticos contra Supabase

## Objetivo

Confirmar que o backend usa o Supabase em runtime apos a recarga de dados e que
os scripts criticos e invariantes minimos de teste continuam coerentes com o
contrato atual de conexao.

## Resultado de Negocio Mensuravel

- a API sobe e responde usando o Supabase como banco alvo
- scripts criticos continuam coerentes com `DIRECT_URL` e `DATABASE_URL`
- o fallback de testes com SQLite permanece preservado

## Contexto Arquitetural

- `backend/app/db/database.py` concentra o contrato de runtime e o fallback de testes
- `scripts/dev_backend.sh` e o launcher oficial da API a partir da raiz do repo
- `backend/scripts/seed_common.py` centraliza a preferencia por `DIRECT_URL` em operacoes sensiveis
- `backend/tests/test_alembic_single_head.py` segue como validacao automatizada minima do historico Alembic

## Definition of Done do Epico
- [x] runtime do backend validado com Supabase
- [ ] scripts criticos revisados contra o novo contrato operacional
- [ ] fallback de testes com SQLite preservado

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Validar runtime do backend com Supabase | Comprovar que a API sobe e responde com o Supabase como banco de runtime | 3 | done | [ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase.md](./issues/ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase.md) |
| ISSUE-F3-01-002 | Validar scripts criticos e invariantes de teste | Confirmar os contratos de scripts sensiveis e do fallback SQLite em testes | 2 | todo | [ISSUE-F3-01-002-Validar-Scripts-Criticos-e-Invariantes-de-Teste.md](./issues/ISSUE-F3-01-002-Validar-Scripts-Criticos-e-Invariantes-de-Teste.md) |

## Artifact Minimo do Epico

- backend validado em runtime usando o Supabase
- scripts criticos revisados contra o contrato operacional atual
- evidencia minima de que o fallback de testes continua isolado em SQLite

## Dependencias
- [Intake](../INTAKE-SUPABASE.md)
- [PRD](../PRD-SUPABASE.md)
- [Fase](./F3_SUPABASE_EPICS.md)
- [F2](../F2-Migracao-de-Dados/F2_SUPABASE_EPICS.md)
