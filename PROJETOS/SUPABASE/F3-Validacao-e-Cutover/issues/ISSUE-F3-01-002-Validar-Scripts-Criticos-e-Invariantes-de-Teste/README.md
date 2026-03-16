---
doc_id: "ISSUE-F3-01-002-Validar-Scripts-Criticos-e-Invariantes-de-Teste"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-002 - Validar scripts criticos e invariantes de teste

## User Story

Como mantenedor do backend, quero validar os scripts criticos e o fallback de
testes apos o cutover do banco, para manter coerencia entre operacao em
Supabase e testes isolados em SQLite.

## Contexto Tecnico

`backend/scripts/seed_common.py` concentra a preferencia por `DIRECT_URL` para
scripts sensiveis de banco. Ao mesmo tempo, `backend/app/db/database.py` deve
manter o fallback SQLite quando `TESTING=true`. Esta issue garante que essas
duas frentes continuam coerentes apos a migracao do banco.

## Plano TDD
- Red: falhar se scripts sensiveis apontarem para um contrato de URL incoerente ou se o fallback SQLite regredir
- Green: validar os scripts criticos contra o contrato atual e confirmar o fallback de testes
- Refactor: consolidar um checklist minimo de manutencao para o estado pos-cutover

## Criterios de Aceitacao
- Given scripts criticos do backend, When o contrato de conexao for revisado, Then eles permanecem coerentes com `DIRECT_URL` e `DATABASE_URL`
- Given `TESTING=true`, When o backend resolve a URL de banco para testes, Then o fallback continua em SQLite
- Given a revisao encerrada, When a fase final for documentada, Then existe evidencia minima de que operacao e testes continuam coerentes

## Definition of Done da Issue
- [x] scripts criticos revisados contra o contrato atual de conexao
- [x] fallback SQLite de testes confirmado
- [x] evidencias minimas de manutencao consolidadas

## Tasks

- [T1: Revisar scripts criticos contra o contrato atual de conexao](./TASK-1.md)
- [T2: Validar fallback SQLite quando TESTING=true](./TASK-2.md)
- [T3: Consolidar evidencias minimas para a fase documental](./TASK-3.md)

## Arquivos Reais Envolvidos

- `backend/scripts/seed_common.py`
- `backend/scripts/seed_domains.py`
- `backend/scripts/seed_sample.py`
- `backend/app/db/database.py`
- `backend/tests/test_alembic_single_head.py`
- `backend/.env.example`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Checklist minimo comprovando coerencia entre scripts criticos, Supabase em
operacao e SQLite em testes.

## Dependencias

- [Intake](../../../INTAKE-SUPABASE.md)
- [Epic](../../EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
- [Fase](../../F3_SUPABASE_EPICS.md)
- [PRD](../../../PRD-SUPABASE.md)
- [ISSUE-F3-01-001](../ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase/)
