---
doc_id: "EPIC-F3-01-EXECUCAO-ASSISTIDA-COM-AUTONOMIA-CONTROLADA.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
---

# EPIC-F3-01 - Execucao assistida com autonomia controlada

## Objetivo

Selecionar a proxima unidade elegivel, executar com contexto suficiente e aplicar gates humanos quando necessario.

## Resultado de Negocio Mensuravel

Reduzir a operacao manual para colocar o projeto em movimento com seguranca e previsibilidade.

## Feature de Origem

- **Feature**: Feature 4
- **Comportamento coberto**: work orders, politica de autonomia, contexto de execucao, bloqueios e evidencias operacionais

## Contexto Arquitetural

O embriao atual do `framework` ja executa uma `next task` simplificada; este epic precisa transformá-lo em fluxo governado por work order e autonomia configuravel.

## Definition of Done do Epico
- [ ] a proxima unidade elegivel pode ser selecionada, executada e acompanhada com historico consultavel

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Selecionar a proxima unidade elegivel com contexto completo | Modelar preflight, contexto e selecao da unidade elegivel. | 5 | todo | [ISSUE-F3-01-001-SELECIONAR-A-PROXIMA-UNIDADE-ELEGIVEL-COM-CONTEXTO-COMPLETO](./issues/ISSUE-F3-01-001-SELECIONAR-A-PROXIMA-UNIDADE-ELEGIVEL-COM-CONTEXTO-COMPLETO/) | Feature 4 |
| ISSUE-F3-01-002 | Executar com autonomia configuravel e acompanhamento operacional | Integrar disparo, override humano e evidencias operacionais. | 5 | todo | [ISSUE-F3-01-002-EXECUTAR-COM-AUTONOMIA-CONFIGURAVEL-E-ACOMPANHAMENTO-OPERACIONAL](./issues/ISSUE-F3-01-002-EXECUTAR-COM-AUTONOMIA-CONFIGURAVEL-E-ACOMPANHAMENTO-OPERACIONAL/) | Feature 4 |

## Artifact Minimo do Epico

Work order valido e painel operacional da proxima acao recomendada.

## Dependencias
- [Intake](../INTAKE-FW5.md)
- [PRD](../PRD-FW5.md)
- [Fase](./F3_FW5_EPICS.md)
- dependencias_operacionais: F2-PLANEJAMENTO-EXECUTAVEL aprovada
