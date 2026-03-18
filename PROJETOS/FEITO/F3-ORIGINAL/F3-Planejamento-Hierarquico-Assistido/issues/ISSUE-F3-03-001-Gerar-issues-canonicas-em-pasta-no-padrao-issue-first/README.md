---
doc_id: "ISSUE-F3-03-001-Gerar-issues-canonicas-em-pasta-no-padrao-issue-first"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-03-001 - Gerar issues canonicas em pasta no padrao issue-first

## User Story

Como PM do FRAMEWORK3, quero gerar issues canonicas em pasta no padrao issue-first para passos 11 e 12 do algoritmo cobertos com issue canonica em pasta.

## Contexto Tecnico

O modulo precisa materializar a governanca issue-first em vez de depender do formato legado de issue em arquivo unico. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Gerar issues canonicas em pasta no padrao issue-first"
- Green: alinhamento minimo do recorte para entregar geracao de issue canonica em pasta disponivel no framework3
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Gerar issues canonicas em pasta no padrao issue-first" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then geracao de issue canonica em pasta disponivel no FRAMEWORK3.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Gerar issue canonica em pasta](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_issue_first_generation.py`

## Artifact Minimo

Geracao de issue canonica em pasta disponivel no FRAMEWORK3.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F3-03-Planejamento-de-Issues-Tasks-e-Instrucoes-TDD.md)
- [Fase](../../F3_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F3-02-002
