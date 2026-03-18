---
doc_id: "ISSUE-F4-01-002-Preparar-sessao-operacional-e-preflight-de-bloqueios"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-01-002 - Preparar sessao operacional e preflight de bloqueios

## User Story

Como PM do FRAMEWORK3, quero preparar sessao operacional e preflight de bloqueios para sessao operacional preenchida apenas para tasks elegiveis.

## Contexto Tecnico

Antes de executar qualquer task o modulo precisa impedir avancos com artefatos ou estados incompletos. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Preparar sessao operacional e preflight de bloqueios"
- Green: alinhamento minimo do recorte para entregar preflight e payload de sessao operacional funcionando
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Preparar sessao operacional e preflight de bloqueios" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then preflight e payload de sessao operacional funcionando.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Preparar sessao operacional e barrar preflights invalidos](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_execution_preflight.py`

## Artifact Minimo

Preflight e payload de sessao operacional funcionando.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F4-01-Selecao-da-Unidade-Executavel-e-Work-Order.md)
- [Fase](../../F4_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F4-01-001
