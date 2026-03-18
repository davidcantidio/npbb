---
doc_id: "ISSUE-F1-03-001-Definir-maquina-de-estados-e-gates-HITL-do-orquestrador"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-03-001 - Definir maquina de estados e gates HITL do orquestrador

## User Story

Como PM do FRAMEWORK3, quero definir maquina de estados e gates hitl do orquestrador para estados e gates operacionais sem ambiguidade no dominio framework.

## Contexto Tecnico

Com o contrato canonico fechado o servico de orquestracao precisa explicitar estados validos invalidos e pontos obrigatorios de intervencao humana. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Definir maquina de estados e gates HITL do orquestrador"
- Green: alinhamento minimo do recorte para entregar maquina de estados e gates hitl refletidos em modelos schemas e orquestrador
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Definir maquina de estados e gates HITL do orquestrador" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then maquina de estados e gates HITL refletidos em modelos schemas e orquestrador.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Aplicar maquina de estados e gates HITL no dominio](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_state_transitions.py`

## Artifact Minimo

Maquina de estados e gates HITL refletidos em modelos schemas e orquestrador.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F1-03-Contrato-do-AgentOrchestrator-e-Modos-de-Operacao.md)
- [Fase](../../F1_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-01-002
