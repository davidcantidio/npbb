---
doc_id: "EPIC-F4-01-Selecao-da-Unidade-Executavel-e-Work-Order.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F4-01 - Selecao da Unidade Executavel e Work Order

## Objetivo

Escolher a proxima task elegivel montar o execution scope e barrar preflights invalidos antes da execucao.

## Resultado de Negocio Mensuravel

O modulo sabe exatamente qual e a proxima unidade executavel e quando nao deve avancar.

## Contexto Arquitetural

O algoritmo operacional depende de determinismo na escolha da task corrente e de um payload executavel consistente.

## Definition of Done do Epico
- [ ] resolvedor de proxima task elegivel funcionando
- [ ] execution scope e work order disponiveis por API
- [ ] preflight bloqueia tasks e issues nao elegiveis

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F4-01-001 | Selecionar proxima task elegivel e montar work order executavel | Proxima task elegivel determinada sem ambiguidade e work order executavel disponivel por API. | 2 | todo | [ISSUE-F4-01-001-Selecionar-proxima-task-elegivel-e-montar-work-order-executavel](./issues/ISSUE-F4-01-001-Selecionar-proxima-task-elegivel-e-montar-work-order-executavel/) |
| ISSUE-F4-01-002 | Preparar sessao operacional e preflight de bloqueios | Sessao operacional preenchida apenas para tasks elegiveis. | 1 | todo | [ISSUE-F4-01-002-Preparar-sessao-operacional-e-preflight-de-bloqueios](./issues/ISSUE-F4-01-002-Preparar-sessao-operacional-e-preflight-de-bloqueios/) |

## Artifact Minimo do Epico

Unidade executavel selecionada e pronta para o orquestrador.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F4_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- F3 concluida
