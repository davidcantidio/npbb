---
doc_id: "ISSUE-F2-02-003-Expor-CRUD-de-issue-task-e-transicoes-de-aprovacao"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-003 - Expor CRUD de issue task e transicoes de aprovacao

## User Story

Como PM do FRAMEWORK3, quero expor crud de issue task e transicoes de aprovacao para crud profundo do framework3 e transicoes de aprovacao disponiveis por api.

## Contexto Tecnico

O recorte profundo precisa refletir o formato issue-first e as transicoes de aprovacao aprovadas em F1. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Expor CRUD de issue task e transicoes de aprovacao"
- Green: alinhamento minimo do recorte para entregar endpoints de issue task e aprovacao operando no backend
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Expor CRUD de issue task e transicoes de aprovacao" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then endpoints de issue task e aprovacao operando no backend.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Expor endpoints de issue e task](./TASK-1.md)
- [T2 - Expor transicoes de aprovacao e status por API](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_issue_task_api.py`
- `backend/tests/test_framework_approval_api.py`

## Artifact Minimo

Endpoints de issue task e aprovacao operando no backend.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F2-02-APIs-e-Servicos-CRUD-Hierarquicos.md)
- [Fase](../../F2_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F2-01-002, ISSUE-F1-03-001
