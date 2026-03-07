---
doc_id: "EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# EPIC-F1-01 - Fundo Tematico e Container Principal

## Objetivo

Criar o componente wrapper `FullPageBackground` que aplica o gradiente e o overlay grafico do template como layer fixa cobrindo 100vw × 100vh, usando os tokens ja fornecidos por `buildLandingTheme` e `renderGraphicOverlay`.

## Resultado de Negocio Mensuravel

O fundo tematico da landing page e calculado inteiramente por CSS/SVG, sem requisicoes de imagem externa, e preenche a viewport completa em qualquer breakpoint. Cada um dos 7 templates exibe fundo visualmente distinto.

## Contexto Arquitetural

- `buildLandingTheme(data)` ja fornece os tokens de cor e gradiente por template
- `renderGraphicOverlay(data)` ja fornece o overlay grafico como elemento React
- o overlay precisa ser reposicionado como layer `fixed` ou `absolute` com z-index 0
- o wrapper deve ser o elemento mais externo da landing page, substituindo o container atual
- referencia: `frontend/src/components/landing/LandingPageView.tsx`

## Definition of Done do Epico

- [ ] componente FullPageBackground renderiza gradiente full-page para os 7 templates
- [ ] renderGraphicOverlay posicionado como layer de fundo sem quebrar em novo container
- [ ] nenhuma imagem externa carregada para compor o fundo
- [ ] fundo preenche 100vw × 100vh sem gap ou cor padrao do browser

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Criar FullPageBackground | Implementar o wrapper que aplica gradiente + overlay como fundo fixo da viewport | 3 | todo | [ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND.md](./issues/ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND.md) |
| ISSUE-F1-01-002 | Adaptar renderGraphicOverlay | Reposicionar renderGraphicOverlay como layer fixa dentro do FullPageBackground | 3 | todo | [ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY.md](./issues/ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY.md) |

## Artifact Minimo do Epico

- `frontend/src/components/landing/FullPageBackground.tsx`

## Dependencias

- [PRD](../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Fase](./F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND]]`
- `[[./issues/ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY]]`
- `[[../PRD-LANDING-FORM-ONLY-v1.0]]`
