---
doc_id: "ISSUE-F3-02-002-EXPOR-TIMELINE-AUDITAVEL-E-FOLLOW-UPS-RASTREAVEIS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-002 - Expor timeline auditavel e follow-ups rastreaveis

## User Story

Como PM, quero consultar timeline, aprovacoes, outputs e follow-ups do projeto para auditar o FW5 sem depender de leitura fragmentada.

## Feature de Origem

- **Feature**: Feature 5
- **Comportamento coberto**: timeline operacional, drilldown de evidencias e follow-ups rastreaveis

## Contexto Tecnico

Depois de review e gate formal, o modulo precisa consolidar historico operacional, prompts, diffs e follow-ups em consultas administrativas navegaveis.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem timeline, filtros e drilldown dos follow-ups
- Green: alinhar dominio API e UI para historico auditavel de ponta a ponta
- Refactor: consolidar consultas e componentes sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given execucoes, aprovacoes e reviews registrados, When a timeline for consultada, Then eventos aparecem ordenados e filtraveis
- Given follow-ups existentes, When o PM abrir um item, Then origem, destino, evidencias e estado ficam visiveis
- Given a issue concluida, When o historico do projeto for revisado, Then prompts, outputs, diffs e evidencias ficam acessiveis no mesmo fluxo

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Modelar timeline, eventos e filtros](./TASK-1.md)
- [T2 - Consolidar leitura auditavel de aprovacoes, prompts, outputs e diffs](./TASK-2.md)
- [T3 - Expor timeline e drilldown de follow-ups ao PM](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_governance_flow.py`
- `backend/tests/test_framework_timeline.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkTimelinePage.tsx`
- `frontend/src/components/dashboard/FrameworkTimeline.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkTimelinePage.test.tsx`

## Artifact Minimo

Timeline auditavel do projeto com drilldown de follow-ups e evidencias.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F3-02-GOVERNANCA-FINAL-E-HISTORICO-AUDITAVEL.md)
- [Fase](../../F3_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F3-02-001
