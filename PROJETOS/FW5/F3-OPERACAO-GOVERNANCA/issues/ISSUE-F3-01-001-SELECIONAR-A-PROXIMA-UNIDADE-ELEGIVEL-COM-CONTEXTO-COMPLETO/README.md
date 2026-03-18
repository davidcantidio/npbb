---
doc_id: "ISSUE-F3-01-001-SELECIONAR-A-PROXIMA-UNIDADE-ELEGIVEL-COM-CONTEXTO-COMPLETO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-001 - Selecionar a proxima unidade elegivel com contexto completo

## User Story

Como PM, quero que o FW5 identifique a proxima unidade elegivel com contexto completo para iniciar a execucao sem violar dependencias ou gates.

## Feature de Origem

- **Feature**: Feature 4
- **Comportamento coberto**: work order, contexto de execucao e preflight de elegibilidade

## Contexto Tecnico

O backend ja possui um `execute_next_task` simplificado; esta issue precisa formalizar work order, contexto de execucao e preflight de elegibilidade a partir da hierarquia planejada.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem work order, elegibilidade e proxima acao
- Green: alinhar modelos servicos API e UI para selecao governada da unidade elegivel
- Refactor: consolidar contratos operacionais sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given backlog executavel pronto, When o sistema calcular a proxima unidade elegivel, Then dependencias, gates e `task_instruction_mode` sao respeitados
- Given uma unidade elegivel, When o contexto for montado, Then work order, escopo e bloqueios ficam claros
- Given a issue concluida, When o PM abrir o painel operacional, Then a proxima acao recomendada fica visivel

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Modelar work order, contexto e preflight de elegibilidade](./TASK-1.md)
- [T2 - Implementar selecao da proxima unidade elegivel](./TASK-2.md)
- [T3 - Entregar painel de proxima acao e bloqueios](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_execution_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkExecutionPage.tsx`
- `frontend/src/components/dashboard/FrameworkNextActionCard.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`

## Artifact Minimo

Work order pronto e painel da proxima unidade elegivel visivel ao PM.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F3-01-EXECUCAO-ASSISTIDA-COM-AUTONOMIA-CONTROLADA.md)
- [Fase](../../F3_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F2-01-002
