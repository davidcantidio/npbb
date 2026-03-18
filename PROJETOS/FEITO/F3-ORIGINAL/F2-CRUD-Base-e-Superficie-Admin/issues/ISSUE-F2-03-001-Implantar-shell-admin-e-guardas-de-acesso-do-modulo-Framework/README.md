---
doc_id: "ISSUE-F2-03-001-Implantar-shell-admin-e-guardas-de-acesso-do-modulo-Framework"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-03-001 - Implantar shell admin e guardas de acesso do modulo Framework

## User Story

Como PM do FRAMEWORK3, quero implantar shell admin e guardas de acesso do modulo framework para entrada protegida do modulo framework disponivel no dashboard.

## Contexto Tecnico

A interface do modulo precisa respeitar o modelo de autenticacao existente e abrir uma rota protegida antes das telas de operacao. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Implantar shell admin e guardas de acesso do modulo Framework"
- Green: alinhamento minimo do recorte para entregar regra minima de acesso aprovada e shell admin disponivel no frontend
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Implantar shell admin e guardas de acesso do modulo Framework" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then regra minima de acesso aprovada e shell admin disponivel no frontend.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Definir recorte de acesso do modulo admin](./TASK-1.md)
- [T2 - Implantar shell e rota protegida do modulo](./TASK-2.md)

## Arquivos Reais Envolvidos
- `frontend/src/store/auth.tsx`
- `frontend/src/components/ProtectedRoute.tsx`
- `frontend/src/app/AppRoutes.tsx`
- `backend/app/core/auth.py`
- `frontend/src/pages/framework/FrameworkHomePage.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkRouting.test.tsx`

## Artifact Minimo

Regra minima de acesso aprovada e shell admin disponivel no frontend.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F2-03-Modulo-Admin-Integrado-ao-Dashboard.md)
- [Fase](../../F2_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F2-02-001, ISSUE-F1-03-002
