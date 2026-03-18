---
doc_id: "ISSUE-F5-01-002-Orquestrar-follow-ups-de-hold-e-retomada-da-fase"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F5-01-002 - Orquestrar follow ups de hold e retomada da fase

## User Story

Como PM do FRAMEWORK3, quero orquestrar follow ups de hold e retomada da fase para hold e remediacao de auditoria seguem a governanca e preservam a retomada segura da fase.

## Contexto Tecnico

Uma auditoria em hold precisa abrir follow-ups bloqueantes e impedir a retomada precoce da fase. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Orquestrar follow ups de hold e retomada da fase"
- Green: alinhamento minimo do recorte para entregar fluxo de hold remediacao e retomada implementado
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Orquestrar follow ups de hold e retomada da fase" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then fluxo de hold remediacao e retomada implementado.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Orquestrar remediacao de hold e retomada da fase](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_hold_remediation.py`

## Artifact Minimo

Fluxo de hold remediacao e retomada implementado.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F5-01-Auditoria-de-Fase-e-Remediacao-de-Hold.md)
- [Fase](../../F5_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F5-01-001
