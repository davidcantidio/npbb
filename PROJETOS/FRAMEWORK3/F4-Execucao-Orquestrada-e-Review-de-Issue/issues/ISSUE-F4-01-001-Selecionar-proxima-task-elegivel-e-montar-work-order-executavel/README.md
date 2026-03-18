---
doc_id: "ISSUE-F4-01-001-Selecionar-proxima-task-elegivel-e-montar-work-order-executavel"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-01-001 - Selecionar proxima task elegivel e montar work order executavel

## User Story

Como PM do FRAMEWORK3, quero selecionar proxima task elegivel e montar work order executavel para proxima task elegivel determinada sem ambiguidade e work order executavel disponivel por api.

## Contexto Tecnico

A fase operacional comeca determinando qual task realmente pode ser executada e qual payload precisa ser entregue ao orquestrador. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Selecionar proxima task elegivel e montar work order executavel"
- Green: alinhamento minimo do recorte para entregar resolvedor de proxima task e endpoint de execution scope funcionando
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Selecionar proxima task elegivel e montar work order executavel" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then resolvedor de proxima task e endpoint de execution scope funcionando.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Selecionar a proxima task elegivel](./TASK-1.md)
- [T2 - Expor execution scope e work order por API](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_next_task_selection.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_execution_scope_api.py`

## Artifact Minimo

Resolvedor de proxima task e endpoint de execution scope funcionando.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F4-01-Selecao-da-Unidade-Executavel-e-Work-Order.md)
- [Fase](../../F4_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F3-04-002, ISSUE-F1-03-002
