---
doc_id: "ISSUE-F1-01-007-Sincronizar-Cascata-Documental-do-Fechamento-da-F1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-007 - Sincronizar cascata documental do fechamento da F1

## User Story

Como revisor da F1, quero sincronizar a cascata documental de fechamento apos a
`ISSUE-F1-01-006`, para que o epico e o manifesto da fase reflitam sem
ambiguidade que a F1 concluiu suas issues e aguarda auditoria.

## Contexto Tecnico

Esta issue nasce da revisao pos-issue de `ISSUE-F1-01-006`.

Rastreabilidade obrigatoria desta issue:
- issue de origem: `ISSUE-F1-01-006`
- evidencia usada na revisao: `BASE_COMMIT=worktree`, `git diff` de
  `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
  e
  `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`,
  leitura de
  `PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md`,
  `backend/tests/test_alembic_env_contract.py`,
  `backend/tests/test_alembic_single_head.py`,
  alem da reexecucao de
  `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py tests/test_alembic_single_head.py`
  e
  `cd backend && TESTING=true python3 -m alembic heads`
- sintoma observado: o epico pai ficou `active` com a `ISSUE-F1-01-006`
  duplicada na tabela, uma vez como `todo` e outra como `done`; o manifesto da
  fase ficou com `audit_gate: "not_ready"` no frontmatter e `gate_atual: pending`
  no corpo
- risco de nao corrigir: a F1 permanece documentalmente incoerente para
  auditoria e planejamento da F2; leituras automatizadas ou humanas podem
  inferir incorretamente que ainda existe issue aberta ou que a fase nao esta
  pronta para auditoria

Escopo desta correcao:
- sincronizar apenas a cascata documental local `issue -> epico -> fase`
  afetada pelo fechamento da `ISSUE-F1-01-006`
- remover a duplicidade da `ISSUE-F1-01-006` na tabela do epico e recalcular o
  status do epico para `done`
- alinhar o manifesto da fase para refletir `EPIC-F1-01` como `done` e o
  `audit_gate` da F1 como `pending`, de forma consistente entre frontmatter,
  corpo e checklist local
- nao reabrir a `ISSUE-F1-01-006`
- nao alterar sprint, `AUDIT-LOG`, F2 ou qualquer contrato funcional do Alembic

## Plano TDD

- Red: evidenciar por leitura e diff que a cascata documental apos a
  `ISSUE-F1-01-006` esta inconsistente entre epico e fase
- Green: corrigir os manifestos do epico e da fase para refletirem o fechamento
  real da issue e a prontidao da F1 para auditoria
- Refactor: manter a remediacao minima e local, sem alterar artefatos fora da
  cascata documental necessaria

## Criterios de Aceitacao

- Given a `ISSUE-F1-01-006` ja esta `done`, When o `EPIC-F1-01` for lido, Then
  existe apenas uma linha para essa issue e o status do epico aparece como
  `done`
- Given todas as issues do `EPIC-F1-01` estao `done`, When o manifesto da fase
  F1 for lido, Then a linha do epico aparece como `done` e o gate da fase fica
  consistente em `pending` entre frontmatter e corpo
- Given o manifesto da fase reflete a transicao `not_ready -> pending`, When a
  checklist local for lida, Then ela nao contradiz o estado final do gate
- Given o follow-up for concluido, When um revisor ler apenas os artefatos
  atualizados, Then ele consegue verificar que a F1 aguarda auditoria sem
  ambiguidade documental
- Given esta issue e apenas documental, When ela for executada, Then nenhum
  contrato funcional do Alembic ou teste backend e alterado

## Definition of Done da Issue

- [x] tabela `Issues do Epico` sem duplicidade da `ISSUE-F1-01-006`
- [x] `EPIC-F1-01` com status `done` coerente com suas issues filhas
- [x] `F1_SUPABASE_EPICS.md` coerente entre frontmatter, corpo e tabela de
      epicos sobre o estado `pending`
- [x] issue de origem e evidencias desta revisao permanecem rastreaveis nesta
      issue
- [x] nenhum arquivo de codigo ou contrato funcional do Alembic foi alterado

## Tasks

- [T1: corrigir manifesto do epico](./TASK-1.md)
- [T2: sincronizar manifesto da fase F1](./TASK-2.md)
- [T3: validar coerencia documental final](./TASK-3.md)

## Arquivos Reais Envolvidos

- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`

## Artifact Minimo

- epico F1 sem duplicidade da `ISSUE-F1-01-006`
- `EPIC-F1-01` marcado como `done`
- manifesto da fase F1 coerente com `audit_gate: pending` e `gate_atual: pending`
- rastreabilidade explicita para a review da `ISSUE-F1-01-006`

## Dependencias

- [Intake](../../../INTAKE-SUPABASE.md)
- [Epic](../../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../../F1_SUPABASE_EPICS.md)
- [PRD](../../../PRD-SUPABASE.md)
- [ISSUE-F1-01-006](../ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md)
