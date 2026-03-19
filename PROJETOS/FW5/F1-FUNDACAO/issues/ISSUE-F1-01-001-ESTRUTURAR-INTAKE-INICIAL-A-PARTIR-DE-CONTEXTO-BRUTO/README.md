---
doc_id: "ISSUE-F1-01-001-ESTRUTURAR-INTAKE-INICIAL-A-PARTIR-DE-CONTEXTO-BRUTO"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Estruturar intake inicial a partir de contexto bruto

## User Story

Como PM, quero transformar contexto bruto em intake estruturado para abrir projetos no FW5 sem montagem manual de artefatos.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: intake completo com taxonomias, lacunas conhecidas e checklist de prontidao

## Contexto Tecnico

O backend ja possui modelos e endpoints iniciais do dominio `framework`, mas ainda sem contrato suficiente para intake versionado e sem superficie administrativa correspondente no frontend.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem criacao validacao e leitura do intake
- Green: alinhar modelos servicos API e UI para produzir intake estruturado e navegavel
- Refactor: consolidar nomes e contratos do dominio sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given contexto bruto valido, When o intake for gerado, Then problema publico fluxo escopo metricas riscos e lacunas ficam estruturados sem perder taxonomias
- Given o intake estruturado, When os checks de prontidao forem executados, Then lacunas criticas bloqueiam o avancar para PRD
- Given a issue concluida, When backend e frontend forem revisados, Then o PM consegue abrir um projeto e inspecionar o intake inicial

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Modelar intake, versoes, lacunas e aprovacoes](./TASK-1.md)
- [T2 - Implementar fluxo assistido de geracao e validacao do intake](./TASK-2.md)
- [T3 - Entregar UI assistida com checklist de prontidao](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_domain_contract.py`
- `backend/tests/test_framework_intake_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkIntakePage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkIntakePage.test.tsx`

## Artifact Minimo

Fluxo de intake estruturado com checklist e bloqueio de lacunas criticas.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F1-01-INTAKE-GOVERNADO-DO-PROJETO.md)
- [Fase](../../F1_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: nenhuma
