---
doc_id: "ISSUE-F2-03-003-Expor-timeline-de-execucoes-aprovacoes-e-proxima-acao"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-03-003 - Expor timeline de execucoes aprovacoes e proxima acao

## User Story

Como PM do FRAMEWORK3, quero expor timeline de execucoes aprovacoes e proxima acao para historico operacional e painel de proxima acao visiveis ao pm.

## Contexto Tecnico

A primeira versao util do modulo admin precisa mostrar historico operacional consolidado e o proximo gate relevante. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Expor timeline de execucoes aprovacoes e proxima acao"
- Green: alinhamento minimo do recorte para entregar timeline de execucoes aprovacoes e proxima acao disponivel no frontend
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Expor timeline de execucoes aprovacoes e proxima acao" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then timeline de execucoes aprovacoes e proxima acao disponivel no frontend.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Expor timeline operacional do projeto](./TASK-1.md)

## Arquivos Reais Envolvidos
- `frontend/src/pages/framework/FrameworkTimelinePage.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/pages/framework/__tests__/FrameworkTimeline.test.tsx`

## Artifact Minimo

Timeline de execucoes aprovacoes e proxima acao disponivel no frontend.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F2-03-Modulo-Admin-Integrado-ao-Dashboard.md)
- [Fase](../../F2_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-02-002, ISSUE-F2-03-001
