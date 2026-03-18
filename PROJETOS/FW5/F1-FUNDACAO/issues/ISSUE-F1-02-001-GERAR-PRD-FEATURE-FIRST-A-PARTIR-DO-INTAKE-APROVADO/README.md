---
doc_id: "ISSUE-F1-02-001-GERAR-PRD-FEATURE-FIRST-A-PARTIR-DO-INTAKE-APROVADO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-02-001 - Gerar PRD feature-first a partir do intake aprovado

## User Story

Como PM, quero gerar um PRD `feature-first` a partir do intake aprovado para seguir ao planejamento sem voltar ao modelo `architecture-first`.

## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: derivacao do PRD, estrutura de features e revisao administrativa inicial

## Contexto Tecnico

Com o intake aprovado, o dominio `framework` precisa persistir PRD, features e rastreabilidade de origem, reaproveitando o backend existente e abrindo a primeira pagina administrativa do PRD.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem derivacao do PRD e leitura das features
- Green: alinhar modelos servicos API e UI para gerar e navegar o PRD
- Refactor: consolidar nomes e payloads do dominio sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given intake aprovado, When o PRD for gerado, Then frontmatter, restricoes, riscos e nao-objetivos sao preservados
- Given o PRD gerado, When o PM o visualizar, Then cada feature exibe objetivo comportamento criterios e impactos
- Given a issue concluida, When o estado do projeto for consultado, Then o proximo passo aponta a validacao/aprovacao do PRD

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Modelar PRD, features e rastreabilidade com o intake](./TASK-1.md)
- [T2 - Implementar derivacao do PRD feature-first a partir do intake aprovado](./TASK-2.md)
- [T3 - Entregar UI de geracao e revisao do PRD](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_domain_contract.py`
- `backend/tests/test_framework_prd_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPrdPage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPrdPage.test.tsx`

## Artifact Minimo

PRD `feature-first` gerado a partir do intake aprovado e navegavel no admin.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F1-02-PRD-FEATURE-FIRST-APROVADO.md)
- [Fase](../../F1_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F1-01-002
