---
doc_id: "ISSUE-F1-01-002-Documentar-Arquitetura-Validar-Decisoes.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-01-002 - Documentar Arquitetura e Validar Decisoes

## User Story

Como desenvolvedor, quero definir o breakpoint de colapso, o conteudo da coluna direita nas etapas Evento e Questionario, a biblioteca de drag-and-drop e confirmar a cobertura Tema/Contexto, para que a implementacao F2 tenha decisoes claras.

## Contexto Tecnico

O PRD exige: breakpoint para viewports menores (colapso para coluna unica), conteudo da coluna direita em Evento e Questionario (a definir), biblioteca dnd (verificar se existe; se nao, recomendar), confirmacao de que "Contexto da landing" cobre 100% dos valores do dropdown "Tema" removido. Depende do resultado da ISSUE-F1-01-001.

## Plano TDD

- Red: N/A (issue de discovery/documentacao)
- Green: Decisoes registradas e validadas
- Refactor: Documentar de forma reutilizavel

## Criterios de Aceitacao

- Given viewports menores, When defino breakpoint, Then o valor (ex: 768px, 1024px) esta documentado com justificativa
- Given as etapas Evento e Questionario, When defino conteudo da coluna direita, Then esta documentado o que exibir em cada uma
- Given o codebase, When verifico biblioteca de drag-and-drop, Then esta documentado se existe ou qual lib recomendar (ex: dnd-kit) com aprovacao pendente
- Given TemaSection e LandingContextSection, When comparo valores, Then confirmo que "Contexto da landing" cobre 100% dos valores do "Tema" removido

## Definition of Done da Issue
- [ ] Breakpoint definido e documentado
- [ ] Conteudo da coluna direita Evento e Questionario definido
- [ ] Decisao sobre biblioteca dnd registrada (existente ou recomendacao com aprovacao)
- [ ] Cobertura Tema/Contexto confirmada

## Tasks Decupadas

- [ ] T1: Definir breakpoint de colapso para coluna unica (pesquisar padroes, testar em viewports)
- [ ] T2: Definir conteudo da coluna direita nas etapas Evento e Questionario
- [ ] T3: Verificar existencia de biblioteca dnd no codebase; se nao, recomendar e documentar para aprovacao
- [ ] T4: Comparar TemaSection e LandingContextSection e confirmar cobertura 100%

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/components/TemaSection.tsx`
- `frontend/src/features/event-lead-form-config/components/LandingContextSection.tsx`
- `frontend/package.json`
- `frontend/src/features/event-wizard/EventWizardPage.tsx`
- `frontend/src/pages/EventQuestionario.tsx`

## Artifact Minimo

Documento na issue com: breakpoint, conteudo coluna direita, decisao dnd, confirmacao cobertura Tema/Contexto.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F1-01-Levantamento-Documentacao.md)
- [Fase](../F1_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [ISSUE-F1-01-001](./ISSUE-F1-01-001-Mapear-Componentes-Layout.md) — concluida
