---
doc_id: "ISSUE-F4-04-001-Sincronizar-cascata-documental-e-persistida-apos-execucao"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-04-001 - Sincronizar cascata documental e persistida apos execucao

## User Story

Como PM do FRAMEWORK3, quero sincronizar cascata documental e persistida apos execucao para cascata `issue -> epic -> fase -> sprint` sincronizada apos execucao e review.

## Contexto Tecnico

A utilidade operacional do FRAMEWORK3 depende de manter coerente a cascata de status entre todos os niveis da hierarquia. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Sincronizar cascata documental e persistida apos execucao"
- Green: alinhamento minimo do recorte para entregar derivacao de status e reabertura por follow-up tratadas no backend
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Sincronizar cascata documental e persistida apos execucao" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then derivacao de status e reabertura por follow-up tratadas no backend.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Sincronizar cascata de status apos execucao e review](./TASK-1.md)
- [T2 - Validar derivacao de status e reabertura por follow-up](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_status_cascade.py`
- `backend/tests/test_framework_status_derivation.py`

## Artifact Minimo

Derivacao de status e reabertura por follow-up tratadas no backend.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F4-04-Sincronizacao-de-Estado-e-Notificacao-HITL.md)
- [Fase](../../F4_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F4-03-002
