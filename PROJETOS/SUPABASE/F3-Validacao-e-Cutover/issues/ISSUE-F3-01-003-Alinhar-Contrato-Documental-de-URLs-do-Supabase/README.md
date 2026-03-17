---
doc_id: "ISSUE-F3-01-003-Alinhar-Contrato-Documental-de-URLs-do-Supabase.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-003 - Alinhar contrato documental de URLs do Supabase

## User Story

Como operador do backend, quero que a documentacao de runtime e deploy
descreva o contrato correto entre `DATABASE_URL` e `DIRECT_URL`, para evitar
configuracao ambigua apos o cutover para o Supabase.

## Contexto Tecnico

- issue de origem: `ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase`
- evidencia usada na revisao: `backend/app/db/database.py`, `scripts/dev_backend.sh`, `backend/.env.example`, `docs/DEPLOY_RENDER_CLOUDFLARE.md`, `docs/TROUBLESHOOTING.md`, smoke com `./scripts/dev_backend.sh`, `GET /health`, `GET /eventos/1/landing` e `backend/tests/test_alembic_single_head.py`
- sintoma observado: a consolidacao documental da F3 passou a aceitar `DATABASE_URL` como "conexao direta ou pooler" e mostrou exemplo com `DATABASE_URL` e `DIRECT_URL` ambos em `:5432`, contrariando o contrato operacional registrado na fase
- risco de nao corrigir: operadores podem configurar o runtime com URL direta por equivalencia indevida, enfraquecendo a separacao entre runtime e operacoes sensiveis e reintroduzindo drift entre runbook, troubleshooting e ambiente real

## Plano TDD
- Red: localizar os trechos documentais que contradizem o contrato confirmado em `backend/.env.example` e no runtime validado
- Green: corrigir redacao e exemplos para deixar explicito que `DATABASE_URL` e usada pela API e `DIRECT_URL` fica reservada a migrations/seed
- Refactor: consolidar um checklist curto para evitar nova ambiguidade entre deploy, troubleshooting e contrato real

## Criterios de Aceitacao
- Given o contrato atual de conexao do backend, When `docs/TROUBLESHOOTING.md` for revisado, Then exemplos e instrucoes deixam explicito o papel de `DATABASE_URL` e `DIRECT_URL` sem ambiguidade
- Given a consolidacao documental da F3, When `docs/DEPLOY_RENDER_CLOUDFLARE.md` for atualizado, Then o estado operacional validado nao afirma mais que o runtime usa "conexao direta ou pooler" de forma indiferenciada
- Given a issue concluida, When a validacao final de consistencia for feita, Then `backend/.env.example`, `docs/TROUBLESHOOTING.md` e `docs/DEPLOY_RENDER_CLOUDFLARE.md` permanecem coerentes entre si

## Definition of Done da Issue
- [x] `docs/TROUBLESHOOTING.md` alinhado ao contrato atual de `DATABASE_URL` e `DIRECT_URL`
- [x] `docs/DEPLOY_RENDER_CLOUDFLARE.md` corrigido sem ambiguidade sobre runtime vs conexao direta
- [x] validacao final de coerencia executada contra `backend/.env.example` e `backend/app/db/database.py`

## Tasks

- [T1: Corrigir exemplos e instrucoes do troubleshooting](./TASK-1.md)
- [T2: Corrigir a consolidacao de deploy e runtime](./TASK-2.md)
- [T3: Validar coerencia final do contrato documental](./TASK-3.md)

## Arquivos Reais Envolvidos

- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `backend/.env.example`
- `backend/app/db/database.py`
- `scripts/dev_backend.sh`

## Artifact Minimo

Runbook de runtime/deploy sem drift sobre o uso de `DATABASE_URL` e `DIRECT_URL`
no cutover para Supabase.

## Dependencias

- [Intake](../../../INTAKE-SUPABASE.md)
- [PRD](../../../PRD-SUPABASE.md)
- [Fase](../../F3_SUPABASE_EPICS.md)
- [Epic](../../EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
- [ISSUE-F3-01-001](../ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase/)
