---
doc_id: "ISSUE-F2-01-002-Consolidar-persistencia-de-issue-task-e-agent-execution"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-002 - Consolidar persistencia de issue task e agent execution

## User Story

Como PM do FRAMEWORK3, quero consolidar persistencia de issue task e agent execution para persistencia estavel do nivel operacional do framework3 com schemas coerentes.

## Contexto Tecnico

O segundo bloco de persistencia cobre a parte operacional do FRAMEWORK3 e prepara os dados usados pelo orquestrador e pela review. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Consolidar persistencia de issue task e agent execution"
- Green: alinhamento minimo do recorte para entregar models schemas e migration do nivel operacional alinhados ao contrato aprovado
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Consolidar persistencia de issue task e agent execution" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then models schemas e migration do nivel operacional alinhados ao contrato aprovado.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Consolidar models de issue task e agent execution](./TASK-1.md)
- [T2 - Consolidar schemas de issue task e agent execution](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py`
- `backend/tests/test_framework_execution_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_execution_schemas.py`

## Artifact Minimo

Models schemas e migration do nivel operacional alinhados ao contrato aprovado.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F2-01-Persistencia-do-Dominio-de-Projetos.md)
- [Fase](../../F2_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-02-002, ISSUE-F1-03-001
