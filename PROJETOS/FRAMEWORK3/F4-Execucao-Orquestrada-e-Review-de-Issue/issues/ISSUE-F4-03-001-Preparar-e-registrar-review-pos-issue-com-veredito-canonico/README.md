---
doc_id: "ISSUE-F4-03-001-Preparar-e-registrar-review-pos-issue-com-veredito-canonico"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-03-001 - Preparar e registrar review pos issue com veredito canonico

## User Story

Como PM do FRAMEWORK3, quero preparar e registrar review pos issue com veredito canonico para review pos-issue disponivel com veredito canonico em backend e frontend.

## Contexto Tecnico

Concluir a execucao de uma issue nao basta. O FRAMEWORK3 precisa de review formal com veredito e evidencias antes de fechar a cadeia operacional. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Preparar e registrar review pos issue com veredito canonico"
- Green: alinhamento minimo do recorte para entregar review pos-issue implementado no backend e na ui
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Preparar e registrar review pos issue com veredito canonico" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then review pos-issue implementado no backend e na UI.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Expor contrato de review pos-issue por API](./TASK-1.md)
- [T2 - Entregar UI de review pos-issue](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_review_issue_api.py`
- `frontend/src/pages/framework/FrameworkIssueReviewPage.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkIssueReviewPage.test.tsx`

## Artifact Minimo

Review pos-issue implementado no backend e na UI.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F4-03-Review-Pos-Issue-e-Follow-ups.md)
- [Fase](../../F4_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F4-02-002
