---
doc_id: "ISSUE-F2-01-001-DERIVAR-FASES-E-EPICOS-A-PARTIR-DAS-FEATURES-DO-PRD"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-001 - Derivar fases e epicos a partir das features do PRD

## User Story

Como PM, quero que o FW5 derive fases e epicos a partir das features aprovadas para iniciar a execucao sem remontar o backlog manualmente.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: derivacao de fases e epicos, IDs estaveis e mapa inicial do projeto

## Contexto Tecnico

Com o PRD aprovado, o dominio `framework` precisa sair da criacao basica de fase unica e passar a refletir a cadeia canonica do projeto com dependencias explicitas.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem derivacao de fases/epicos e seus IDs
- Green: alinhar modelos servicos API e UI para criar e ler o mapa inicial do projeto
- Refactor: consolidar nomenclaturas e serializacao sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given um PRD aprovado, When o planejamento iniciar, Then fases e epicos sao derivados a partir das features do PRD
- Given a hierarquia criada, When o PM navegar pelo mapa do projeto, Then IDs, dependencias e `Feature de Origem` ficam visiveis
- Given a issue concluida, When a estrutura for revisada, Then nao resta drift para agrupamento por camada tecnica

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Modelar fases, epicos, IDs e dependencias](./TASK-1.md)
- [T2 - Derivar fases e epicos a partir das features](./TASK-2.md)
- [T3 - Expor mapa administrativo de fases e epicos](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_planning_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPlanningPage.tsx`
- `frontend/src/components/dashboard/FrameworkProjectMap.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`

## Artifact Minimo

Mapa administrativo com fases e epicos derivados do PRD aprovado.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F2-01-PLANEJAMENTO-EXECUTAVEL-RASTREAVEL.md)
- [Fase](../../F2_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F1-02-002
