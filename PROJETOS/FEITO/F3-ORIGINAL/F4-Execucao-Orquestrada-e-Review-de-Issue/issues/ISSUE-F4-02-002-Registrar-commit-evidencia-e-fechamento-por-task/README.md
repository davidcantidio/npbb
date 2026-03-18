---
doc_id: "ISSUE-F4-02-002-Registrar-commit-evidencia-e-fechamento-por-task"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-02-002 - Registrar commit evidencia e fechamento por task

## User Story

Como PM do FRAMEWORK3, quero registrar commit evidencia e fechamento por task para task so encerra com rastreabilidade minima de commit e evidencia.

## Contexto Tecnico

O fluxo de execucao precisa exigir um minimo de evidencias por task antes de permitir o encerramento operacional. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Registrar commit evidencia e fechamento por task"
- Green: alinhamento minimo do recorte para entregar validacao de commit e evidencia por task aplicada ao fluxo operacional
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Registrar commit evidencia e fechamento por task" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then validacao de commit e evidencia por task aplicada ao fluxo operacional.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Exigir commit e evidencia no fechamento da task](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_commit_evidence.py`

## Artifact Minimo

Validacao de commit e evidencia por task aplicada ao fluxo operacional.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F4-02-Execucao-Sequencial-de-Tasks-por-Orquestrador.md)
- [Fase](../../F4_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F4-02-001
