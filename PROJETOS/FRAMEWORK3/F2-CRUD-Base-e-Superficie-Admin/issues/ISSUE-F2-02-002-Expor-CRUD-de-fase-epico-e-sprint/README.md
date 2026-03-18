---
doc_id: "ISSUE-F2-02-002-Expor-CRUD-de-fase-epico-e-sprint"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-002 - Expor CRUD de fase epico e sprint

## User Story

Como PM do FRAMEWORK3, quero expor crud de fase epico e sprint para crud do planejamento intermediario disponivel por api com limites de sprint observaveis.

## Contexto Tecnico

O backend precisa expor o recorte intermediario do planejamento respeitando os limites de sprint da governanca. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Expor CRUD de fase epico e sprint"
- Green: alinhamento minimo do recorte para entregar endpoints de `phase/epic/sprint` funcionando com validacao de capacidade
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Expor CRUD de fase epico e sprint" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then endpoints de `phase/epic/sprint` funcionando com validacao de capacidade.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Expor endpoints de fase epico e sprint](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_phase_epic_sprint_api.py`

## Artifact Minimo

Endpoints de `phase/epic/sprint` funcionando com validacao de capacidade.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F2-02-APIs-e-Servicos-CRUD-Hierarquicos.md)
- [Fase](../../F2_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F2-01-001
