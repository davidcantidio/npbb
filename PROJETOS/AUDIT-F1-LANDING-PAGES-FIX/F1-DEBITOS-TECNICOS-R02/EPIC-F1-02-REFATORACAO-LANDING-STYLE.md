---
doc_id: "EPIC-F1-02-REFATORACAO-LANDING-STYLE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F1-02 - Refatoracao Estrutural landingStyle

## Objetivo

Decompor o arquivo monolitico `landingStyle.tsx` (752 linhas) em modulos coesos e remover campos mortos de `LayoutVisualSpec` (achados S-01 e S-02 da auditoria F1-R02).

## Resultado de Negocio Mensuravel

Arquivo landingStyle.tsx com no maximo 25 linhas. LayoutVisualSpec sem campos sem consumidor. tsc e suite de testes da landing passando sem regressao.

## Contexto Arquitetural

- `frontend/src/components/landing/landingStyle.tsx` concentra tema, layout, overlays e helpers de card
- Estrutura alvo: `landingTheme.ts`, `landingOverlays.tsx`, `landingLayout.ts`, `landingCardStyles.ts`, `landingStyle.tsx` (re-exports)
- Campos mortos a remover: heroBackground, heroMinHeight, heroGridColumns, heroTextCardBackground, heroTextCardBorder, contentGridColumns, imageMinHeight
- Campo a renomear: heroTextColor -> pageTextColor (consumido por LandingPreviewBadge)

## Definition of Done do Epico

- [ ] landingTheme.ts contem buildLandingTheme, buildFormCardTheme, tokens e helpers
- [ ] landingOverlays.tsx contem renderGraphicOverlay e renderers por template
- [ ] landingLayout.ts contem LayoutVisualSpec e getLayoutVisualSpec
- [ ] landingCardStyles.ts contem getCardPaperSx
- [ ] landingStyle.tsx tem no maximo 25 linhas (re-exports)
- [ ] LayoutVisualSpec sem campos mortos; heroTextColor renomeado para pageTextColor
- [ ] tsc --noEmit passa
- [ ] Todos os testes frontend da landing passam

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Decompor landingStyle em modulos especializados | Criar landingTheme, landingOverlays, landingLayout, landingCardStyles e re-export shim | 5 | todo | [ISSUE-F1-02-001-DECOMPOR-LANDING-STYLE.md](./issues/ISSUE-F1-02-001-DECOMPOR-LANDING-STYLE.md) |
| ISSUE-F1-02-002 | Limpar LayoutVisualSpec de campos mortos | Remover campos hero nao consumidos e renomear heroTextColor para pageTextColor | 3 | done | [ISSUE-F1-02-002-LIMPAR-LAYOUT-VISUAL-SPEC.md](./issues/ISSUE-F1-02-002-LIMPAR-LAYOUT-VISUAL-SPEC.md) |

## Artifact Minimo do Epico

- `frontend/src/components/landing/landingTheme.ts`
- `frontend/src/components/landing/landingOverlays.tsx`
- `frontend/src/components/landing/landingLayout.ts`
- `frontend/src/components/landing/landingCardStyles.ts`
- `frontend/src/components/landing/landingStyle.tsx` (refatorado)

## Dependencias

- [PRD](../PRD-DEBITOS-TECNICOS-R02-v1.0.md)
- [Fase](./F1_AUDIT_F1_LANDING_PAGES_FIX_EPICS.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F1-02-001-DECOMPOR-LANDING-STYLE]]`
- `[[./issues/ISSUE-F1-02-002-LIMPAR-LAYOUT-VISUAL-SPEC]]`
- `[[../PRD-DEBITOS-TECNICOS-R02-v1.0]]`
