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

## Resultado do Discovery

### T1 - Componentes de preview identificados

Componentes e hook confirmados nos arquivos citados pela issue:

- `EventLeadFormConfigPage`: pagina de configuracao que monta o fluxo e insere o host de preview entre as secoes do formulario
- `PreviewSection`: componente host do preview interno na tela de configuracao; renderiza titulo, acoes, estados de loading/erro e o container `data-testid="event-lead-preview-host"`
- `LandingPageView`: renderer visual da landing; recebe `data` e e usado pelo `PreviewSection` com `mode="preview"`
- `useLandingPreview`: hook responsavel por carregar e atualizar o `LandingPageData` consumido pelo `PreviewSection`

Distincao funcional registrada:

- host de preview na tela de configuracao: `PreviewSection`
- renderer da landing em si: `LandingPageView`
- abastecimento de dados do preview: `useLandingPreview`

### T2 - Estrutura atual de layout

Na `EventLeadFormConfigPage`, o conteudo principal da configuracao fica dentro de um `Paper elevation={2}` com `sx={{ p: 3, borderRadius: 3 }}`.

Quando a configuracao esta carregada, a pagina usa `Stack spacing={2}` como estrutura principal de composicao. Nao ha `Grid` nem layout side-by-side neste nivel.

Ordem atual das secoes no fluxo vertical:

1. `TemaSection`
2. `LandingContextSection`
3. `PreviewSection`
4. `GovernanceSection`
5. `CamposSection`
6. `Divider`
7. `UrlsSection`

Conclusao de layout:

- a pagina atual usa composicao vertical baseada em `Stack`
- o preview nao fica fixo em coluna lateral
- o preview aparece intercalado no meio do fluxo do formulario

Observacao local do proprio `PreviewSection`:

- o cabecalho interno usa `Stack` responsivo com `direction={{ xs: "column", md: "row" }}`
- esse ajuste e apenas interno ao cabecalho da secao de preview e nao caracteriza layout geral da pagina em duas colunas

### T3 - Compartilhamento entre contextos

Achados nos arquivos citados:

- `AppRoutes` expone a rota protegida `/eventos/:id/formulario-lead`, que carrega `EventLeadFormConfig`
- nos arquivos citados nao existe segunda pagina de configuracao dedicada para landing page
- `useLandingPreview` busca `LandingPageData` para abastecer o preview interno do fluxo de configuracao
- `PreviewSection` renderiza `LandingPageView data={previewData} mode="preview"`
- `AppRoutes` tambem aponta as rotas de landing para `EventLandingPage`, que representa o contexto publico da landing

Decisao registrada:

- nao ha evidencia, nos arquivos citados, de uma segunda pagina de configuracao separada para landing page
- o renderer visual da landing e compartilhado: `LandingPageView`
- o contexto de configuracao e o host do preview interno sao especificos do fluxo de lead form: `EventLeadFormConfigPage` + `PreviewSection` + `useLandingPreview`
- portanto, nao se trata de um unico componente compartilhado para tudo; o compartilhamento ocorre no renderer da landing, enquanto o shell de configuracao/preview interno e especifico da tela de configuracao

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
