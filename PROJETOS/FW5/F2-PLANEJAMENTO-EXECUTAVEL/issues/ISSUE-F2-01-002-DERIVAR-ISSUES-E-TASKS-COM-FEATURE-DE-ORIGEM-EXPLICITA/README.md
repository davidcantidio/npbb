---
doc_id: "ISSUE-F2-01-002-DERIVAR-ISSUES-E-TASKS-COM-FEATURE-DE-ORIGEM-EXPLICITA"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-002 - Derivar issues e tasks com Feature de Origem explicita

## User Story

Como PM, quero que o FW5 derive issues e tasks com dependencia e `Feature de Origem` explicitas para transformar o PRD em backlog executavel.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: derivacao de issues, tasks, elegibilidade basica e metadados de sprint

## Contexto Tecnico

Depois da derivacao de fases e epicos, o dominio precisa descer a granularidade para issue/task sem perder limites canonicos nem a ligacao com o PRD.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem derivacao de issues/tasks e leitura detalhada da hierarquia
- Green: alinhar modelos servicos API e UI para completar o backlog executavel
- Refactor: consolidar payloads e navegacao sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given epicos derivados, When issues e tasks forem geradas, Then cada item carrega `Feature de Origem`, dependencias e metadados minimos
- Given a hierarquia completa, When o PM navegar pelos detalhes, Then backlog e limites canonicos ficam claros
- Given a issue concluida, When a elegibilidade basica for consultada, Then a proxima unidade executavel ja pode ser inferida sem ambiguidade documental

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Modelar issues, tasks, dependencias e metadados de sprint](./TASK-1.md)
- [T2 - Derivar issues e tasks com Feature de Origem e elegibilidade](./TASK-2.md)
- [T3 - Expor navegacao e leitura detalhada da hierarquia](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_planning_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPlanningPage.tsx`
- `frontend/src/components/dashboard/FrameworkHierarchyTree.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`

## Artifact Minimo

Hierarquia completa com issues e tasks derivadas do PRD e pronta para a F3.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F2-01-PLANEJAMENTO-EXECUTAVEL-RASTREAVEL.md)
- [Fase](../../F2_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F2-01-001
