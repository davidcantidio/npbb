---
doc_id: "ISSUE-F1-02-002-VALIDAR-RASTREABILIDADE-E-GATE-DE-APROVACAO-DO-PRD"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-02-002 - Validar rastreabilidade e gate de aprovacao do PRD

## User Story

Como PM, quero validar o gate de aprovacao do PRD com historico e bloqueios para seguir ao planejamento executavel sem drift documental.

## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: validacao estrutural, gate de aprovacao e historico do PRD

## Contexto Tecnico

O FW5 precisa garantir que o PRD so siga ao planejamento quando mantiver rastreabilidade com o intake, estrutura por feature e historico de aprovacao consultavel.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem validacoes estruturais e gate do PRD
- Green: alinhar dominio API e UI para aprovar bloquear ou ajustar o PRD com historico
- Refactor: consolidar mensagens e estados do gate sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given um PRD gerado, When a validacao estrutural rodar, Then faltas de feature, criterio ou origem bloqueiam aprovacao
- Given o PM aprova o PRD, When o status do projeto for consultado, Then o proximo passo aponta ao planejamento executavel
- Given novas revisoes do PRD, When o historico for aberto, Then versoes, diffs e aprovadores ficam consultaveis

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Validar estrutura, criterios por feature e bloqueios do PRD](./TASK-1.md)
- [T2 - Fechar gate de aprovacao do PRD com status e historico visiveis](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_prd_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPrdReviewPage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPrdReviewPage.test.tsx`

## Artifact Minimo

Gate do PRD com validacao estrutural, aprovacao e historico rastreaveis.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F1-02-PRD-FEATURE-FIRST-APROVADO.md)
- [Fase](../../F1_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F1-02-001
