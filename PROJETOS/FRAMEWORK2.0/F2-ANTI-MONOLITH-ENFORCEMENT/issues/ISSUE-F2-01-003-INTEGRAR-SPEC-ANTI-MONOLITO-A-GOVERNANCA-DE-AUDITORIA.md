---
doc_id: "ISSUE-F2-01-003-INTEGRAR-SPEC-ANTI-MONOLITO-A-GOVERNANCA-DE-AUDITORIA.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-01-003 - Integrar spec anti-monolito a governanca de auditoria

## User Story

Como auditor do framework, quero que a governanca de auditoria aponte para o
spec anti-monolito para manter thresholds em uma unica fonte.

## Contexto Tecnico

Sem esta integracao, o risco e voltar a duplicar limites em prompt, template e
governanca. O destino correto e `GOV-AUDITORIA.md`.

## Plano TDD

- Red: localizar onde a auditoria ainda poderia carregar thresholds localmente.
- Green: apontar a governanca para `SPEC-ANTI-MONOLITO.md`.
- Refactor: revisar a consistencia entre governanca, prompt e template.

## Criterios de Aceitacao

- Given `GOV-AUDITORIA.md`, When for lido, Then fica explicito que os
  thresholds estruturais sao lidos do spec
- Given o fluxo de auditoria, When houver achado de monolito, Then o spec e a
  fonte normativa usada no julgamento
- Given a integracao concluida, When houver mudanca futura de threshold, Then a
  alteracao exige manutencao em um unico arquivo

## Definition of Done da Issue

- [ ] governanca de auditoria aponta para o spec
- [ ] nao ha duplicacao de threshold na regra de auditoria
- [ ] referencias cruzadas minimas revisadas

## Tasks Decupadas

- [ ] T1: revisar `GOV-AUDITORIA.md` em busca de thresholds duplicados
- [ ] T2: apontar a regra para `SPEC-ANTI-MONOLITO.md`
- [ ] T3: revisar impacto em `PROMPT-AUDITORIA.md`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-AUDITORIA.md`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
- `PROJETOS/COMUM/PROMPT-AUDITORIA.md`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-AUDITORIA.md`

## Dependencias

- [Issue 001](./ISSUE-F2-01-001-DEFINIR-THRESHOLDS-ANTI-MONOLITO-POR-LINGUAGEM.md)
- [Issue 002](./ISSUE-F2-01-002-CALIBRAR-THRESHOLDS-USANDO-DASHBOARD-LEADS-ETARIA.md)
- [Epic](../EPIC-F2-01-SPEC-ANTI-MONOLITO.md)
- [Fase](../F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
