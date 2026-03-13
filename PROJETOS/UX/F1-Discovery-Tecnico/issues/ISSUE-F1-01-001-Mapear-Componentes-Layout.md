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

## Registro de Discovery

### T1 - Componentes de preview mapeados

#### Landing

- Cadeia de preview atual: `EventLeadFormConfigPage -> useLandingPreview -> PreviewSection -> MobilePreviewFrame -> LandingPageView`
- `EventLeadFormConfigPage` monta `previewPayload`, chama `useLandingPreview(...)` e injeta `preview.previewData`, `preview.previewLoading`, `preview.previewError` e `preview.refreshPreview` em `PreviewSection`
- `useLandingPreview` busca os dados via `previewEventoLanding(...)` e controla `previewData`, `previewLoading` e `previewError`
- `PreviewSection` renderiza o host visual do preview e, quando ha dados, encapsula `LandingPageView` dentro de `MobilePreviewFrame`
- `MobilePreviewFrame` define o frame mobile fixo do preview com largura base de `390px` e altura base de `844px`
- `LandingPageView` e o componente que renderiza a landing em `mode="preview"`

#### Ativacao

- Nao existe hoje um preview mobile side-by-side embutido em `EventAtivacoesPage`
- A pagina atual renderiza `AtivacaoFormSection` e `AtivacoesTable`
- A visualizacao detalhada existente fica em `AtivacaoViewDialog`
- O componente visual real usado no dialog e `AtivacaoQrPreview`
- O estado atual da etapa de ativacoes e: visualizacao modal com metadados, URLs e QR code; nao ha componente equivalente a `MobilePreviewFrame + LandingPageView` para pagina publica de ativacao dentro do layout principal

### T2 - Layout atual de EventLeadFormConfigPage

- Shell: `EventWizardPageShell width="wide"` com `EventWizardStepper activeStep={1}`
- Container principal do conteudo: `Paper elevation={2}` com `p: 3` e `borderRadius: 3`
- Layout interno principal: `Box` com `display: "grid"`
- Modo desktop (`md` para cima): `gridTemplateColumns: "minmax(0, 1fr) minmax(390px, 430px)"`
- Modo mobile/tablet menor que `md`: `gridTemplateColumns: "minmax(0, 1fr)"`, empilhando painel e preview
- Gap entre colunas/blocos: `{ xs: 3, xl: 4 }`
- Coluna esquerda: `Stack spacing={2}` com `maxWidth: 760` no desktop
- Ordem das secoes da coluna esquerda:
  1. `TemaSection`
  2. `LandingContextSection`
  3. `GovernanceSection`
  4. `CamposSection`
  5. `Divider`
  6. `UrlsSection`
- Coluna direita: `Box` com `maxWidth: 430`
- Comportamento da coluna direita no desktop: `position: "sticky"` com `top: theme.spacing(3)` e `justifySelf: "end"`
- Comportamento da coluna direita fora do desktop: `position: "static"` e largura total
- Conteudo da coluna direita: `PreviewSection`, que por sua vez renderiza o frame mobile da landing
- Classificacao do layout: CSS Grid no container macro + Stack/Flex interno nas secoes

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F1-01-Levantamento-Documentacao.md)
- [Fase](../F1_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
