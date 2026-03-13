---
doc_id: "ISSUE-F2-02-001-ADICIONAR-SECAO-DE-COMPLEXIDADE-ESTRUTURAL-AO-TEMPLATE-DE-AUDITORIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-02-001 - Adicionar secao de complexidade estrutural ao template de auditoria

## User Story

Como auditor, quero uma secao canonica para registrar complexidade estrutural e
thresholds excedidos de forma comparavel entre rodadas.

## Contexto Tecnico

Esta issue expande `TEMPLATE-AUDITORIA-RELATORIO.md` para acomodar achados de
monolito e seus indicadores associados.

## Plano TDD

- Red: identificar lacunas do template atual para registrar monolito.
- Green: incluir uma secao dedicada a complexidade estrutural.
- Refactor: revisar se os campos permitem comparacao entre rodadas.

## Criterios de Aceitacao

- Given o template de auditoria, When for lido, Then existe secao explicita de
  complexidade estrutural
- Given um achado de monolito, When o template for preenchido, Then os
  thresholds excedidos podem ser registrados sem improviso
- Given rodadas sucessivas, When os relatorios forem comparados, Then os dados
  estruturais ficam consistentes

## Definition of Done da Issue

- [x] secao de complexidade estrutural presente no template
- [x] thresholds e indicadores suportados no layout
- [x] comparacao entre rodadas viavel

## Tasks Decupadas

- [x] T1: desenhar os campos minimos da secao estrutural
- [x] T2: integrar os campos ao template de relatorio
- [x] T3: revisar a utilidade para rodadas subsequentes

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## Artifact Minimo

- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`

## Dependencias

- [Epic](../EPIC-F2-02-METRICAS-NO-TEMPLATE-DE-AUDITORIA.md)
- [Fase](../F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
