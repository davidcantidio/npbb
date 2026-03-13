---
doc_id: "ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-01-001 - Checklist de Regressao Multiviewport

## User Story

Como PM, quero um checklist de regressao executado em todas as etapas e viewports, para garantir que a refatoracao nao introduziu bugs antes do deploy.

## Contexto Tecnico

A F2 alterou layout, removiu redundancias e implementou drag-and-drop. A validacao manual deve cobrir: Evento, Formulario de Lead, Gamificacao, Ativacoes, Questionario; viewports desktop (1024px+), tablet (768px), mobile (390px); fluxo de criacao e edicao; reatividade do preview; persistencia ao salvar.

## Plano TDD

- Red: N/A (issue de validacao manual)
- Green: Checklist executado; resultados documentados
- Refactor: Consolidar achados em relatorio

## Criterios de Aceitacao

- Given cada etapa do wizard, When executo fluxo de configuracao, Then nao ha regressao funcional
- Given viewports desktop, tablet e mobile, When visualizo cada etapa, Then layout se comporta corretamente
- Given Formulario de Lead, When edito campos e arrasto ordem, Then preview atualiza e persistencia funciona
- Given o checklist completo, When PM revisa, Then aprova ou identifica itens bloqueantes

## Definition of Done da Issue
- [ ] Checklist por etapa executado
- [ ] Validacao multiviewport executada
- [ ] Resultados documentados na issue ou artefato
- [ ] PM aprovou ou follow-ups identificados

## Tasks Decupadas

- [ ] T1: Executar checklist de regressao na etapa Evento (desktop, tablet, mobile)
- [ ] T2: Executar checklist na etapa Formulario de Lead (layout, preview, dnd, redundancias removidas)
- [ ] T3: Executar checklist nas etapas Gamificacao, Ativacoes e Questionario
- [ ] T4: Documentar resultados e obter aprovacao do PM

## Arquivos Reais Envolvidos

- Todas as paginas do wizard
- `frontend/src/features/event-lead-form-config/`
- `frontend/src/pages/EventGamificacao.tsx`
- `frontend/src/pages/EventAtivacoes.tsx`
- `frontend/src/pages/EventQuestionario.tsx`
- `frontend/src/features/event-wizard/EventWizardPage.tsx`

## Artifact Minimo

Checklist preenchido com resultados por etapa e viewport; registro de aprovacao PM.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F3-01-Validacao-Regressao.md)
- [Fase](../F3_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [F2](../../../F2-Implementacao/F2_UX_EPICS.md) — concluida
