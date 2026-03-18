---
doc_id: "ISSUE-F3-04-001-Persistir-prompts-outputs-aprovacoes-e-evidencias-do-planejamento"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-04-001 - Persistir prompts outputs aprovacoes e evidencias do planejamento

## User Story

Como PM do FRAMEWORK3, quero persistir prompts outputs aprovacoes e evidencias do planejamento para historico completo do planejamento persistido e visivel no modulo.

## Contexto Tecnico

O planejamento assistido so atende ao PRD se cada prompt output aprovacao e evidencia deixar trilha persistida e consultavel. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Persistir prompts outputs aprovacoes e evidencias do planejamento"
- Green: alinhamento minimo do recorte para entregar historico do planejamento persistido no backend e exibido no frontend
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Persistir prompts outputs aprovacoes e evidencias do planejamento" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then historico do planejamento persistido no backend e exibido no frontend.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Persistir historico do planejamento por etapa](./TASK-1.md)
- [T2 - Expor historico do planejamento no frontend](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/app/models/framework_models.py`
- `backend/tests/test_framework_planning_history.py`
- `frontend/src/pages/framework/FrameworkHistoryPage.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkHistoryPage.test.tsx`

## Artifact Minimo

Historico do planejamento persistido no backend e exibido no frontend.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F3-04-Historico-de-Aprovacoes-e-Artefatos-Canonicos.md)
- [Fase](../../F3_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-02-002, ISSUE-F3-03-003
