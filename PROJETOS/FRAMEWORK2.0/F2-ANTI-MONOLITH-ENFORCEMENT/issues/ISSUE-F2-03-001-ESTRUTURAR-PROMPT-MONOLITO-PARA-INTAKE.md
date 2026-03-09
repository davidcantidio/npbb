---
doc_id: "ISSUE-F2-03-001-ESTRUTURAR-PROMPT-MONOLITO-PARA-INTAKE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-03-001 - Estruturar prompt monolito para intake

## User Story

Como auditor, quero um prompt que converta um achado estrutural em intake para
remediacao sem perder rastreabilidade de origem.

## Contexto Tecnico

Esta issue cria `PROMPT-MONOLITO-PARA-INTAKE.md`, definindo entrada minima,
validacoes e saida esperada compativel com `TEMPLATE-INTAKE.md`.

## Plano TDD

- Red: listar quais dados do achado estrutural precisam sobreviver ao intake.
- Green: estruturar o prompt com input, validacoes e output.
- Refactor: revisar aderencia ao template canonico de intake.

## Criterios de Aceitacao

- Given o prompt de monolito, When for lido, Then os inputs obrigatorios estao
  explicitos
- Given um achado estrutural, When o prompt for executado, Then o output
  esperado e um intake rastreavel
- Given a sessao futura de auditoria, When precisar acionar remediacao, Then o
  prompt fornece um handoff claro

## Definition of Done da Issue

- [ ] prompt estruturado com entradas minimas
- [ ] output esperado alinhado ao template de intake
- [ ] rastreabilidade para auditoria de origem prevista

## Tasks Decupadas

- [ ] T1: definir dados de entrada obrigatorios
- [ ] T2: estruturar o fluxo e o output esperado do prompt
- [ ] T3: revisar aderencia a `TEMPLATE-INTAKE.md`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
- `PROJETOS/COMUM/TEMPLATE-INTAKE.md`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## Artifact Minimo

- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`

## Dependencias

- [Issue 001](./ISSUE-F2-01-001-DEFINIR-THRESHOLDS-ANTI-MONOLITO-POR-LINGUAGEM.md)
- [Epic](../EPIC-F2-03-PROMPT-MONOLITO-PARA-INTAKE.md)
- [Fase](../F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
