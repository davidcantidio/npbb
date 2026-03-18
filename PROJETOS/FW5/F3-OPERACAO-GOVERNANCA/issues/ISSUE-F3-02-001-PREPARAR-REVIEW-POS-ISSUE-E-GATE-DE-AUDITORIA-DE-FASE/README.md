---
doc_id: "ISSUE-F3-02-001-PREPARAR-REVIEW-POS-ISSUE-E-GATE-DE-AUDITORIA-DE-FASE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-001 - Preparar review pos-issue e gate de auditoria de fase

## User Story

Como PM, quero revisar uma issue concluida e formalizar o gate de auditoria da fase para manter a governanca efetiva no FW5.

## Feature de Origem

- **Feature**: Feature 5
- **Comportamento coberto**: review pos-issue, vereditos, destinos de follow-up e gate de auditoria da fase

## Contexto Tecnico

Com a execucao assistida disponivel, o dominio precisa fechar review pos-issue, follow-ups e o gate formal da auditoria de fase com persistencia e leitura administrativa.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem review, gate e follow-ups
- Green: alinhar dominio API e UI para veredito, roteamento e status de auditoria
- Refactor: consolidar contratos de governanca sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given uma issue concluida, When o PM registrar review, Then veredito, evidencias e follow-up ficam persistidos
- Given uma fase pronta para auditoria, When o gate for atualizado, Then status, relatorio e proxima acao ficam consistentes
- Given a issue concluida, When follow-ups forem consultados, Then origem, destino e estado ficam claros

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Modelar review, auditoria, gate e destinos de follow-up](./TASK-1.md)
- [T2 - Registrar vereditos e roteamento no servico/API](./TASK-2.md)
- [T3 - Entregar fluxo UI de review e auditoria](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_governance_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkGovernancePage.tsx`
- `frontend/src/components/dashboard/FrameworkReviewPanel.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkGovernancePage.test.tsx`

## Artifact Minimo

Review pos-issue e gate de auditoria formalizados com follow-ups rastreaveis.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F3-02-GOVERNANCA-FINAL-E-HISTORICO-AUDITAVEL.md)
- [Fase](../../F3_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F3-01-002
