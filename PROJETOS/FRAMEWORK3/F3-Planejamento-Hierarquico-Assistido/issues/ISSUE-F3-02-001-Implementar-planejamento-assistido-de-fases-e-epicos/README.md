---
doc_id: "ISSUE-F3-02-001-Implementar-planejamento-assistido-de-fases-e-epicos"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-001 - Implementar planejamento assistido de fases e epicos

## User Story

Como PM do FRAMEWORK3, quero implementar planejamento assistido de fases e epicos para passos 5 a 8 do algoritmo cobertos no modulo com geracao e aprovacao de fases e epicos.

## Contexto Tecnico

Com o PRD aprovado o modulo precisa fatiar o projeto em fases e epicos preservando o gate humano. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Implementar planejamento assistido de fases e epicos"
- Green: alinhamento minimo do recorte para entregar fluxo de geracao e aprovacao de fases e epicos disponivel
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Implementar planejamento assistido de fases e epicos" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then fluxo de geracao e aprovacao de fases e epicos disponivel.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Gerar fases e epicos a partir do PRD aprovado](./TASK-1.md)
- [T2 - Implementar revisao e aprovacao de fases e epicos no frontend](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_phase_epic_planning.py`
- `frontend/src/pages/framework/FrameworkPlanningPage.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkPhaseEpicApproval.test.tsx`

## Artifact Minimo

Fluxo de geracao e aprovacao de fases e epicos disponivel.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F3-02-Planejamento-de-Fases-Epicos-e-Sprints.md)
- [Fase](../../F3_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F3-01-002
