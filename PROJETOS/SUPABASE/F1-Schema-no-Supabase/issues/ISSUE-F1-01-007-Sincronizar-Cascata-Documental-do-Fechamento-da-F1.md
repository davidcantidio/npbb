---
doc_id: "ISSUE-F1-01-007-Sincronizar-Cascata-Documental-do-Fechamento-da-F1.md"
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

## Tasks Decupadas

- [x] T1: corrigir o manifesto do epico para refletir o fechamento real da `ISSUE-F1-01-006`
- [x] T2: sincronizar o manifesto da fase F1 com o estado correto do epico e do gate
- [x] T3: validar a coerencia documental final sem reabrir a issue original

## Instructions por Task

### T1
- objetivo: remover a duplicidade da `ISSUE-F1-01-006` no epico e recalcular o
  status do `EPIC-F1-01`
- precondicoes: `ISSUE-F1-01-006` lida; regras de cascata em `GOV-SCRUM.md`
  compreendidas; sem necessidade de alterar a issue de origem
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md`
  - `PROJETOS/COMUM/GOV-SCRUM.md`
- passos_atomicos:
  1. localizar as duas linhas da `ISSUE-F1-01-006` na tabela `Issues do Epico`
  2. remover apenas a linha residual com status `todo`
  3. manter a linha final da issue com status `done`
  4. recalcular o status do epico para `done`, ja que todas as issues filhas
     ficam encerradas
  5. nao alterar objetivo, DoD do epico ou qualquer outra issue da tabela
- comandos_permitidos:
  - `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
  - `rg -n "ISSUE-F1-01-006|status:" PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- resultado_esperado: epico sem duplicidade da issue e com status `done`
- testes_ou_validacoes_obrigatorias:
  - confirmar por leitura que a tabela contem uma unica linha da `ISSUE-F1-01-006`
  - confirmar por leitura que o frontmatter do epico ficou `status: "done"`
- stop_conditions:
  - parar se a correcao exigir reabrir a issue original, alterar sprint ou
    mexer em artefato fora do epico

### T2
- objetivo: alinhar o manifesto da fase F1 ao estado final correto do epico e
  do gate de auditoria
- precondicoes: T1 concluida; estado final do epico confirmado como `done`;
  entendimento das regras de gate em `GOV-SCRUM.md` e `GOV-ISSUE-FIRST.md`
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
  - `PROJETOS/COMUM/GOV-SCRUM.md`
  - `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- passos_atomicos:
  1. atualizar a linha do `EPIC-F1-01` na tabela de epicos para `done`
  2. alinhar o `audit_gate` do frontmatter para `pending`
  3. alinhar a secao `Estado do Gate de Auditoria` para o mesmo estado `pending`
  4. revisar a checklist local `not_ready -> pending` para que ela nao
     contradiga o estado final do gate
  5. nao criar relatorio de auditoria, nao atualizar `AUDIT-LOG` e nao simular
     veredito formal
- comandos_permitidos:
  - `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
  - `rg -n "audit_gate:|gate_atual:|EPIC-F1-01|not_ready -> pending" PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- resultado_esperado: manifesto da fase coerente com a F1 pronta para auditoria
- testes_ou_validacoes_obrigatorias:
  - confirmar por leitura que `audit_gate` e `gate_atual` ficaram ambos `pending`
  - confirmar por leitura que a tabela de epicos mostra `EPIC-F1-01` como `done`
- stop_conditions:
  - parar se a correcao exigir abrir auditoria formal, alterar `AUDIT-LOG` ou
    tratar a fase como `approved`

### T3
- objetivo: validar a coerencia documental final da cascata local
- precondicoes: T1 e T2 concluidas; nenhum arquivo de codigo alterado nesta issue
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md`
- passos_atomicos:
  1. reler os manifestos do epico e da fase apos as edicoes
  2. confirmar que a `ISSUE-F1-01-006` segue `done` e nao foi reaberta
  3. confirmar que o epico ficou `done`, a fase segue `active` e o gate ficou
     `pending`
  4. confirmar que a remediacao permaneceu documental e local
- comandos_permitidos:
  - `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
  - `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
  - `rg -n "ISSUE-F1-01-006|status:|audit_gate:|gate_atual:|EPIC-F1-01" PROJETOS/SUPABASE/F1-Schema-no-Supabase`
- resultado_esperado: cascata documental local consistente e pronta para a
  futura auditoria da F1
- testes_ou_validacoes_obrigatorias:
  - confirmar por leitura que nao existe mais linha `todo` residual da `ISSUE-F1-01-006`
  - confirmar por leitura que o estado final ficou `issue done -> epico done -> fase active + gate pending`
- stop_conditions:
  - parar se surgir necessidade de alterar codigo, testes backend ou documentos
    fora da cascata local desta fase

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

- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../F1_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F1-01-006](./ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md)
