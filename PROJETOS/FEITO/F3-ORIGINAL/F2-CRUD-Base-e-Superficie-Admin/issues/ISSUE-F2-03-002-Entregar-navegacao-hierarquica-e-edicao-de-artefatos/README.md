---
doc_id: "ISSUE-F2-03-002-Entregar-navegacao-hierarquica-e-edicao-de-artefatos"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-03-002 - Entregar navegacao hierarquica e edicao de artefatos

## User Story

Como PM do FRAMEWORK3, quero entregar navegacao hierarquica e edicao de artefatos para hierarquia completa navegavel e artefatos persistidos editaveis no modulo admin.

## Contexto Tecnico

Com o shell admin pronto o PM precisa navegar por projeto fase epico issue task e inspecionar ou editar o artefato selecionado. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Entregar navegacao hierarquica e edicao de artefatos"
- Green: alinhamento minimo do recorte para entregar arvore hierarquica e editor de artefatos funcionando no frontend
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Entregar navegacao hierarquica e edicao de artefatos" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then arvore hierarquica e editor de artefatos funcionando no frontend.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Entregar navegacao hierarquica do projeto](./TASK-1.md)
- [T2 - Entregar detalhe e edicao de artefatos persistidos](./TASK-2.md)

## Arquivos Reais Envolvidos
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/framework/FrameworkProjectPage.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkHierarchy.test.tsx`
- `frontend/src/pages/framework/FrameworkDetailPage.tsx`
- `frontend/src/components/framework/ArtifactEditor.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkArtifactEditor.test.tsx`

## Artifact Minimo

Arvore hierarquica e editor de artefatos funcionando no frontend.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F2-03-Modulo-Admin-Integrado-ao-Dashboard.md)
- [Fase](../../F2_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F2-03-001, ISSUE-F2-02-003
