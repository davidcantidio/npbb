---
doc_id: "EPIC-F3-01-Intake-e-PRD-Assistidos-com-Aprovacao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F3-01 - Intake e PRD Assistidos com Aprovacao

## Objetivo

Cobrir intake e PRD com gates explicitos de aprovacao e rastreabilidade de origem.

## Resultado de Negocio Mensuravel

O modulo conduz os primeiros passos do algoritmo sem perder a aprovacao humana obrigatoria.

## Contexto Arquitetural

Esta etapa cobre o inicio do fluxo definido em `PROJETOS/Algoritmo.md` e prepara a base de planejamento hierarquico assistido.

## Definition of Done do Epico
- [ ] intake assistido com gate de aprovacao funcionando
- [ ] geracao de PRD vinculada ao intake funcionando
- [ ] review e aprovacao de PRD rastreaveis no frontend e backend

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Implementar intake assistido com gate de aprovacao | Passos 1 e 2 do algoritmo cobertos no modulo com gate explicito de aprovacao. | 1 | todo | [ISSUE-F3-01-001-Implementar-intake-assistido-com-gate-de-aprovacao](./issues/ISSUE-F3-01-001-Implementar-intake-assistido-com-gate-de-aprovacao/) |
| ISSUE-F3-01-002 | Implementar geracao de PRD com rastreabilidade do gate | Passos 3 e 4 do algoritmo cobertos no modulo com geracao revisao e aprovacao de PRD. | 2 | todo | [ISSUE-F3-01-002-Implementar-geracao-de-PRD-com-rastreabilidade-do-gate](./issues/ISSUE-F3-01-002-Implementar-geracao-de-PRD-com-rastreabilidade-do-gate/) |

## Artifact Minimo do Epico

Fluxo Intake -> PRD operavel no modulo FRAMEWORK3.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F3_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- F2 concluida
