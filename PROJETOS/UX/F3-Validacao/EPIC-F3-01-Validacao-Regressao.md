---
doc_id: "EPIC-F3-01-Validacao-Regressao.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-14"
---

# EPIC-F3-01 - Validacao e Regressao

## Objetivo

Executar checklist de regressao manual por etapa e viewport, e obter aprovacao do PM para deploy.

## Resultado de Negocio Mensuravel

Zero regressao funcional confirmada; interface aprovada pelo PM para deploy em producao.

## Contexto Arquitetural

As 5 etapas do wizard foram refatoradas em F2. A validacao cobre: fluxo completo de criacao/edicao de evento, configuracao de formulario de lead, gamificacao, ativacoes e questionario; layout em desktop, tablet e mobile; ausencia de elementos removidos; reatividade do preview; drag-and-drop.

## Definition of Done do Epico
- [x] Checklist de regressao executado
- [x] Validacao multiviewport concluida
- [ ] PM aprovou interface

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Checklist de Regressao Multiviewport | Executar checklist por etapa e viewport; documentar resultados | 3 | done | [ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md](./issues/ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md) |

## Artifact Minimo do Epico

Checklist preenchido; registro de aprovacao do PM.

## Resultado da Rodada Atual

Checklist concluido e issue encerrada com evidencias documentadas, mas a interface nao foi aprovada para deploy.
Os bloqueios da rodada ficaram concentrados no `Formulario de Lead`, onde redundancias removidas no escopo da F2 ainda aparecem em tela.

## Dependencias
- [Intake](../../INTAKE-UX.md)
- [PRD](../../PRD-UX.md)
- [Fase](./F3_UX_EPICS.md)
- [F2](../../F2-Implementacao/F2_UX_EPICS.md) — concluida
