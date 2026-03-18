---
doc_id: "EPIC-F3-03-Planejamento-de-Issues-Tasks-e-Instrucoes-TDD.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F3-03 - Planejamento de Issues, Tasks e Instrucoes TDD

## Objetivo

Gerar issues canonicas em pasta tasks required e instrucoes TDD com bloqueio de elegibilidade.

## Resultado de Negocio Mensuravel

Toda issue nova passa a nascer no formato issue-first com detalhamento operacional suficiente para execucao.

## Contexto Arquitetural

Este epic desce o planejamento para o nivel operacional exigido por `task_instruction_mode: required` e pela governanca `issue-first`.

## Definition of Done do Epico
- [ ] issues canonicas em pasta geradas no padrao aprovado
- [ ] tasks required geradas no formato `TASK-N.md`
- [ ] instrucoes TDD e bloqueio BLOQUEADO aplicados quando faltar detalhamento

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-03-001 | Gerar issues canonicas em pasta no padrao issue-first | Passos 11 e 12 do algoritmo cobertos com issue canonica em pasta. | 1 | todo | [ISSUE-F3-03-001-Gerar-issues-canonicas-em-pasta-no-padrao-issue-first](./issues/ISSUE-F3-03-001-Gerar-issues-canonicas-em-pasta-no-padrao-issue-first/) |
| ISSUE-F3-03-002 | Gerar tasks obrigatorias no formato TASK-N.md | Passos 13 e 14 do algoritmo cobertos com tasks required em arquivos proprios. | 1 | todo | [ISSUE-F3-03-002-Gerar-tasks-obrigatorias-no-formato-TASK-N-md](./issues/ISSUE-F3-03-002-Gerar-tasks-obrigatorias-no-formato-TASK-N-md/) |
| ISSUE-F3-03-003 | Gerar instrucoes TDD e validar elegibilidade BLOQUEADO | Passo 15 do algoritmo coberto com instrucoes TDD e bloqueio de elegibilidade. | 2 | todo | [ISSUE-F3-03-003-Gerar-instrucoes-TDD-e-validar-elegibilidade-BLOQUEADO](./issues/ISSUE-F3-03-003-Gerar-instrucoes-TDD-e-validar-elegibilidade-BLOQUEADO/) |

## Artifact Minimo do Epico

Backlog operacional detalhado no padrao issue-first.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F3_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F3-02
