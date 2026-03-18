---
doc_id: "ISSUE-F4-04-002-Notificar-PM-e-expor-proxima-acao-nos-gates-obrigatorios"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-04-002 - Notificar PM e expor proxima acao nos gates obrigatorios

## User Story

Como PM do FRAMEWORK3, quero notificar pm e expor proxima acao nos gates obrigatorios para proxima acao e eventos de gate visiveis ao pm em backend e frontend.

## Contexto Tecnico

A cadeia operacional fecha mostrando explicitamente ao PM o proximo gate ou decisao humana relevante. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Notificar PM e expor proxima acao nos gates obrigatorios"
- Green: alinhamento minimo do recorte para entregar notificacoes de gate e proxima acao integradas ao modulo
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Notificar PM e expor proxima acao nos gates obrigatorios" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then notificacoes de gate e proxima acao integradas ao modulo.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Expor proxima acao e notificacoes de gate](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `frontend/src/pages/framework/FrameworkTimelinePage.tsx`
- `backend/tests/test_framework_next_action_notifications.py`
- `frontend/src/pages/framework/__tests__/FrameworkNextAction.test.tsx`

## Artifact Minimo

Notificacoes de gate e proxima acao integradas ao modulo.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F4-04-Sincronizacao-de-Estado-e-Notificacao-HITL.md)
- [Fase](../../F4_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F4-04-001
