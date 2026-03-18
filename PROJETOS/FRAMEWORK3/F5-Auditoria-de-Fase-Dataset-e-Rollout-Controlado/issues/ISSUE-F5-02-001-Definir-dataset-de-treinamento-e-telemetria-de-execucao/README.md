---
doc_id: "ISSUE-F5-02-001-Definir-dataset-de-treinamento-e-telemetria-de-execucao"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F5-02-001 - Definir dataset de treinamento e telemetria de execucao

## User Story

Como PM do FRAMEWORK3, quero definir dataset de treinamento e telemetria de execucao para contrato do dataset treinavel aprovado e instrumentado no modulo.

## Contexto Tecnico

O PRD declara explicitamente a necessidade de formar um dataset util para treinamento futuro de um LLM especialista em gestao de projetos. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Definir dataset de treinamento e telemetria de execucao"
- Green: alinhamento minimo do recorte para entregar contrato do dataset treinavel definido e instrumentado para extracao
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Definir dataset de treinamento e telemetria de execucao" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then contrato do dataset treinavel definido e instrumentado para extracao.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Definir contrato do dataset treinavel](./TASK-1.md)
- [T2 - Instrumentar persistencia e extracao do dataset](./TASK-2.md)

## Arquivos Reais Envolvidos
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_training_dataset.py`

## Artifact Minimo

Contrato do dataset treinavel definido e instrumentado para extracao.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F5-02-Dataset-de-Treinamento-e-Observabilidade.md)
- [Fase](../../F5_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F3-04-001, ISSUE-F4-04-002
