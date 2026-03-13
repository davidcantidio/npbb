---
doc_id: "ISSUE-F2-03-002-VALIDAR-PROMPT-DE-MONOLITO-CONTRA-TEMPLATE-DE-INTAKE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-03-002 - Validar prompt de monolito contra template de intake

## User Story

Como mantenedor do framework, quero validar o prompt de monolito contra o
template de intake para evitar um fluxo estrutural com output incompleto.

## Contexto Tecnico

Esta issue testa a compatibilidade documental entre
`PROMPT-MONOLITO-PARA-INTAKE.md` e `TEMPLATE-INTAKE.md`.

## Plano TDD

- Red: comparar o output esperado do prompt com os campos do template.
- Green: ajustar lacunas de compatibilidade.
- Refactor: revisar exemplos e instrucoes para reduzir ambiguidade.

## Criterios de Aceitacao

- Given o prompt de monolito, When seu output esperado for comparado ao
  template de intake, Then todos os campos obrigatorios estao cobertos
- Given lacunas detectadas, When a issue for concluida, Then elas estao
  corrigidas no prompt ou no guidance associado
- Given o fluxo auditivo futuro, When acionar remediacao, Then o intake gerado
  pode ser materializado sem completar contexto fora do prompt

## Definition of Done da Issue

- [ ] cobertura total dos campos obrigatorios do intake
- [ ] instrucoes do prompt revisadas
- [ ] fluxo pronto para dependencia de `F3-04` e `F3-05`

## Tasks Decupadas

- [ ] T1: mapear output do prompt contra o template de intake
- [ ] T2: corrigir gaps de cobertura
- [ ] T3: revisar usabilidade do fluxo resultante

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
- `PROJETOS/COMUM/TEMPLATE-INTAKE.md`

## Artifact Minimo

- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`

## Dependencias

- [Issue 001](./ISSUE-F2-03-001-ESTRUTURAR-PROMPT-MONOLITO-PARA-INTAKE.md)
- [Epic](../EPIC-F2-03-PROMPT-MONOLITO-PARA-INTAKE.md)
- [Fase](../F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
