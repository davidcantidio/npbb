---
doc_id: "ISSUE-F5-01-001-Preparar-e-registrar-auditoria-de-fase-com-gate-persistido"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F5-01-001 - Preparar e registrar auditoria de fase com gate persistido

## User Story

Como PM do FRAMEWORK3, quero preparar e registrar auditoria de fase com gate persistido para auditoria de fase operacionalizada com gate persistido no framework3.

## Contexto Tecnico

A fase final conecta o modulo ao `AUDIT-LOG.md` e aos relatorios de auditoria previstos pela governanca. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Preparar e registrar auditoria de fase com gate persistido"
- Green: alinhamento minimo do recorte para entregar contrato de auditoria e fluxo api/ui de rodada de auditoria disponiveis
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Preparar e registrar auditoria de fase com gate persistido" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then contrato de auditoria e fluxo API/UI de rodada de auditoria disponiveis.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Preparar contrato de auditoria de fase](./TASK-1.md)
- [T2 - Expor API e UI para executar rodada de auditoria](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_audit_contract.py`
- `PROJETOS/FRAMEWORK3/AUDIT-LOG.md`
- `backend/app/api/v1/endpoints/framework.py`
- `frontend/src/pages/framework/FrameworkAuditPage.tsx`
- `backend/tests/test_framework_audit_api.py`
- `frontend/src/pages/framework/__tests__/FrameworkAuditPage.test.tsx`

## Artifact Minimo

Contrato de auditoria e fluxo API/UI de rodada de auditoria disponiveis.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F5-01-Auditoria-de-Fase-e-Remediacao-de-Hold.md)
- [Fase](../../F5_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F4-04-002
