---
doc_id: "ISSUE-F4-03-002-Materializar-follow-up-de-review-como-issue-local-ou-new-intake"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-03-002 - Materializar follow up de review como issue local ou new intake

## User Story

Como PM do FRAMEWORK3, quero materializar follow up de review como issue local ou new intake para follow-up pos-review nasce no artefato correto com rastreabilidade explicita.

## Contexto Tecnico

Quando a review reprovar ou limitar o fechamento da issue o modulo precisa escolher corretamente entre issue local e new intake. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Materializar follow up de review como issue local ou new intake"
- Green: alinhamento minimo do recorte para entregar criacao de follow-up pos-review disponivel no backend
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Materializar follow up de review como issue local ou new intake" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then criacao de follow-up pos-review disponivel no backend.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Criar follow-up no destino correto apos a review](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_review_followup.py`

## Artifact Minimo

Criacao de follow-up pos-review disponivel no backend.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F4-03-Review-Pos-Issue-e-Follow-ups.md)
- [Fase](../../F4_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F4-03-001
