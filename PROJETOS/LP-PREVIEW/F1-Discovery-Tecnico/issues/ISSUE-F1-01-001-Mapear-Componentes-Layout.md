---
doc_id: "ISSUE-F1-01-001-Mapear-Componentes-Layout.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-01-001 - Mapear Componentes de Preview e Estrutura de Layout

## User Story

Como desenvolvedor, quero identificar o nome exato dos componentes de preview e a estrutura de layout da pagina de configuracao, para planejar com seguranca a refatoracao em layout side-by-side.

## Contexto Tecnico

O PRD indica lacunas: nome do(s) componente(s) de preview, estrutura de layout (CSS Grid / Flexbox), e se o componente e compartilhado entre leads e landing page. O codebase possui `EventLeadFormConfigPage`, `PreviewSection`, `LandingPageView`, `useLandingPreview`. O preview hoje e intercalado entre blocos em stack vertical.

## Plano TDD

- Red: N/A (issue de discovery/documentacao)
- Green: Informacoes mapeadas e registradas
- Refactor: Organizar documentacao de forma reutilizavel

## Criterios de Aceitacao

- Given o codebase atual, When analiso os arquivos de configuracao de leads e landing page, Then identifico o nome exato do(s) componente(s) de preview
- Given a pagina de configuracao, When analiso o layout, Then documento se usa CSS Grid, Flexbox ou outro e como as secoes estao dispostas
- Given os dois contextos (leads e landing page), When comparo, Then confirmo se o componente de preview e compartilhado ou sao instancias distintas

## Definition of Done da Issue
- [ ] Nome(s) do(s) componente(s) de preview documentado(s)
- [ ] Estrutura de layout atual documentada (Grid/Flex/outro)
- [ ] Decisao sobre compartilhamento entre contextos registrada

## Tasks Decupadas

- [ ] T1: Localizar e listar componentes de preview no codebase (PreviewSection, LandingPageView, etc.)
- [ ] T2: Documentar estrutura de layout da EventLeadFormConfigPage (Paper, Stack, ordem das secoes)
- [ ] T3: Confirmar se existe segunda pagina de config de landing ou se ambos contextos sao o mesmo fluxo

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/features/event-lead-form-config/hooks/useLandingPreview.ts`
- `frontend/src/app/AppRoutes.tsx`

## Artifact Minimo

- Documento na issue ou em artefato anexo com: lista de componentes, estrutura de layout, decisao compartilhamento

## Dependencias

- [Intake](../../INTAKE-LP-PREVIEW.md)
- [Epic](../EPIC-F1-01-Levantamento-Documentacao.md)
- [Fase](../F1_LP-PREVIEW_EPICS.md)
- [PRD](../../PRD-LP-PREVIEW.md)
