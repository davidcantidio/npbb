---
doc_id: "EPIC-F3-01-Validacao-Regressao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F3-01 - Validacao e Regressao

## Objetivo

Executar checklist de regressao manual por etapa e viewport, e obter aprovacao do PM para deploy.

## Resultado de Negocio Mensuravel

Zero regressao funcional confirmada; interface aprovada pelo PM para deploy em producao.

## Contexto Arquitetural

As 5 etapas do wizard foram refatoradas em F2. A validacao cobre: fluxo completo de criacao/edicao de evento, configuracao de formulario de lead, gamificacao, ativacoes e questionario; layout em desktop, tablet e mobile; ausencia de elementos removidos; reatividade do preview; drag-and-drop.

## Definition of Done do Epico
- [ ] Checklist de regressao executado
- [ ] Validacao multiviewport concluida
- [ ] PM aprovou interface

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Checklist de Regressao Multiviewport | Executar checklist por etapa e viewport; documentar resultados | 3 | todo | [ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md](./issues/ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md) |

## Artifact Minimo do Epico

Checklist preenchido; registro de aprovacao do PM.

## Dependencias
- [Intake](../../INTAKE-UX.md)
- [PRD](../../PRD-UX.md)
- [Fase](./F3_UX_EPICS.md)
- [F2](../../F2-Implementacao/F2_UX_EPICS.md) — concluida
