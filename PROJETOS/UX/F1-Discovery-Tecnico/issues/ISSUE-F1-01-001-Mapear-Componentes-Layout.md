---
doc_id: "ISSUE-F1-01-001-Mapear-Componentes-Layout.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-01-001 - Mapear Componentes e Layout

## User Story

Como desenvolvedor, quero identificar o nome exato dos componentes de preview (landing e ativacao) e a estrutura de layout das 5 paginas do wizard, para planejar com seguranca a refatoracao em layout side-by-side.

## Contexto Tecnico

O PRD indica lacunas: nome do(s) componente(s) de preview de landing e de ativacao, estrutura de layout (CSS Grid / Flexbox) de cada pagina do wizard. O codebase possui EventLeadFormConfigPage com PreviewSection, LandingPageView, useLandingPreview. As paginas EventGamificacao, EventAtivacoes, EventQuestionario e EventWizardPage precisam ser mapeadas.

## Plano TDD

- Red: N/A (issue de discovery/documentacao)
- Green: Informacoes mapeadas e registradas
- Refactor: Organizar documentacao de forma reutilizavel

## Criterios de Aceitacao

- Given o codebase atual, When analiso os arquivos das 5 etapas do wizard, Then identifico o nome exato do(s) componente(s) de preview de landing e de ativacao
- Given cada pagina do wizard, When analiso o layout, Then documento se usa CSS Grid, Flexbox ou outro e como as secoes estao dispostas
- Given a estrutura atual, When comparo as 5 paginas, Then identifico padroes comuns e diferencas para planejar layout compartilhado

## Definition of Done da Issue
- [ ] Nome(s) do(s) componente(s) de preview de landing documentado(s)
- [ ] Nome(s) do(s) componente(s) de preview de ativacao documentado(s)
- [ ] Estrutura de layout de cada uma das 5 paginas documentada (Grid/Flex/outro)

## Tasks Decupadas

- [ ] T1: Localizar e listar componentes de preview de landing (EventLeadFormConfig) e de ativacao (EventAtivacoes)
- [ ] T2: Documentar estrutura de layout de EventLeadFormConfigPage (Paper, Stack, ordem das secoes)
- [ ] T3: Documentar estrutura de layout de EventGamificacao, EventAtivacoes, EventQuestionario e EventWizardPage

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/features/event-lead-form-config/hooks/useLandingPreview.ts`
- `frontend/src/pages/EventGamificacao.tsx`
- `frontend/src/pages/EventAtivacoes.tsx`
- `frontend/src/pages/EventQuestionario.tsx`
- `frontend/src/features/event-wizard/EventWizardPage.tsx`

## Artifact Minimo

Documento na issue ou artefato anexo com: lista de componentes de preview, estrutura de layout de cada pagina.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F1-01-Levantamento-Documentacao.md)
- [Fase](../F1_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
