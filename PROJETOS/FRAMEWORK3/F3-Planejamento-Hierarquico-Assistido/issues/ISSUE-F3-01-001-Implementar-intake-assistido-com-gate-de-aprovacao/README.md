---
doc_id: "ISSUE-F3-01-001-Implementar-intake-assistido-com-gate-de-aprovacao"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-001 - Implementar intake assistido com gate de aprovacao

## User Story

Como PM do FRAMEWORK3, quero implementar intake assistido com gate de aprovacao para passos 1 e 2 do algoritmo cobertos no modulo com gate explicito de aprovacao.

## Contexto Tecnico

A fase F3 inicia cobrindo intake com gate humano explicito e rastreabilidade entre backend e frontend. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Implementar intake assistido com gate de aprovacao"
- Green: alinhamento minimo do recorte para entregar fluxo de intake assistido e aprovavel no framework3
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Implementar intake assistido com gate de aprovacao" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then fluxo de intake assistido e aprovavel no FRAMEWORK3.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Implementar fluxo de intake assistido](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/api/v1/endpoints/framework.py`
- `frontend/src/pages/framework/FrameworkIntakePage.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkIntakeFlow.test.tsx`
- `backend/tests/test_framework_intake_flow.py`

## Artifact Minimo

Fluxo de intake assistido e aprovavel no FRAMEWORK3.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F3-01-Intake-e-PRD-Assistidos-com-Aprovacao.md)
- [Fase](../../F3_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F2-03-003
