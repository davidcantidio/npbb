---
doc_id: "ISSUE-F3-02-002-Implementar-planejamento-assistido-de-sprints-com-enforcement-de-limites"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-002 - Implementar planejamento assistido de sprints com enforcement de limites

## User Story

Como PM do FRAMEWORK3, quero implementar planejamento assistido de sprints com enforcement de limites para passos 9 e 10 do algoritmo cobertos no modulo com limites de sprint aplicados.

## Contexto Tecnico

A geracao de sprints precisa respeitar `GOV-SPRINT-LIMITES.md` e bloquear backlog acima da capacidade aprovada. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Implementar planejamento assistido de sprints com enforcement de limites"
- Green: alinhamento minimo do recorte para entregar fluxo de geracao e aprovacao de sprints com enforcement de capacidade disponivel
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Implementar planejamento assistido de sprints com enforcement de limites" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then fluxo de geracao e aprovacao de sprints com enforcement de capacidade disponivel.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Gerar sprints com enforcement de limites](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/api/v1/endpoints/framework.py`
- `frontend/src/pages/framework/FrameworkSprintPlanningPage.tsx`
- `backend/tests/test_framework_sprint_limits.py`
- `frontend/src/pages/framework/__tests__/FrameworkSprintPlanning.test.tsx`

## Artifact Minimo

Fluxo de geracao e aprovacao de sprints com enforcement de capacidade disponivel.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F3-02-Planejamento-de-Fases-Epicos-e-Sprints.md)
- [Fase](../../F3_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F3-02-001
