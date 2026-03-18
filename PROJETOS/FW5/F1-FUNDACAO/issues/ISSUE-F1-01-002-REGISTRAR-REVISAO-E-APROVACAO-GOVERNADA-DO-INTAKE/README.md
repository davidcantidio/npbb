---
doc_id: "ISSUE-F1-01-002-REGISTRAR-REVISAO-E-APROVACAO-GOVERNADA-DO-INTAKE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-002 - Registrar revisao e aprovacao governada do intake

## User Story

Como PM, quero revisar aprovar ou ajustar o intake com historico persistido para seguir ao PRD com governanca rastreavel.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: revisao, diff, aprovacao e historico do intake

## Contexto Tecnico

Depois da geracao do intake, o dominio precisa guardar versoes, diff, aprovador e transicao explicita do gate `Intake -> PRD` sem depender de memoria operacional.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem revisao, diff e aprovacao do intake
- Green: alinhar persistencia, API e UI para historico rastreavel do gate
- Refactor: consolidar eventos e payloads sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given um intake existente, When o PM revisa e aprova, Then versao diff e aprovador ficam persistidos
- Given uma revisao com ajuste, When nova versao for gerada, Then o historico permanece consultavel e ordenado
- Given a aprovacao do intake, When o status do projeto for consultado, Then o proximo passo aponta a derivacao do PRD

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Persistir trilha de revisao, diff e gate Intake -> PRD](./TASK-1.md)
- [T2 - Entregar fluxo UI de revisao e aprovacao com historico](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_intake_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkIntakeReviewPage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkIntakeReviewPage.test.tsx`

## Artifact Minimo

Historico de revisao e aprovacao do intake consultavel e conectado ao gate `Intake -> PRD`.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F1-01-INTAKE-GOVERNADO-DO-PROJETO.md)
- [Fase](../../F1_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F1-01-001
