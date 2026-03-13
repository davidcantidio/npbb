---
doc_id: "ISSUE-F2-02-002-REGISTRAR-DECISION-REFS-E-TENDENCIA-ENTRE-RODADAS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-02-002 - Registrar decision refs e tendencia entre rodadas

## User Story

Como auditor, quero rastrear decisoes estruturais e tendencia entre rodadas
para evitar relatorios isolados e sem contexto de continuidade.

## Contexto Tecnico

Esta issue completa a camada de rastreabilidade do template de auditoria,
formalizando `decision_refs` e leitura comparativa de rounds anteriores.

## Plano TDD

- Red: localizar o que falta para ligar auditoria a decisoes e historico.
- Green: incluir `decision_refs` e tendencia no template canonico.
- Refactor: revisar se o preenchimento continua simples em rodada inicial.

## Criterios de Aceitacao

- Given o template de auditoria, When for lido, Then existe campo para
  `decision_refs`
- Given uma auditoria de segunda rodada, When o template for preenchido, Then a
  tendencia frente a rodadas anteriores pode ser registrada
- Given uma primeira rodada, When o template for usado, Then a ausencia de
  historico nao impede o preenchimento

## Definition of Done da Issue

- [x] `decision_refs` presente no template
- [x] secao de tendencia entre rodadas definida
- [x] preenchimento continua valido sem historico anterior

## Tasks Decupadas

- [x] T1: adicionar `decision_refs` ao template
- [x] T2: criar bloco de tendencia entre rodadas
- [x] T3: revisar compatibilidade com rodada inicial

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
- `PROJETOS/COMUM/GOV-DECISOES.md`

## Artifact Minimo

- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`

## Dependencias

- [Issue 001](./ISSUE-F2-02-001-ADICIONAR-SECAO-DE-COMPLEXIDADE-ESTRUTURAL-AO-TEMPLATE-DE-AUDITORIA.md)
- [Epic](../EPIC-F2-02-METRICAS-NO-TEMPLATE-DE-AUDITORIA.md)
- [Fase](../F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
