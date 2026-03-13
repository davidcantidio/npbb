---
doc_id: "EPIC-F2-02-Frame-Mobile-Breakpoints.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F2-02 - Frame Mobile e Breakpoints

## Objetivo

Aplicar frame visual de celular com viewport ~390px ao preview e implementar tratamento de breakpoint para viewports menores (desktop com resolucao baixa ou tablets), com colapso controlado do layout.

## Resultado de Negocio Mensuravel

Preview simula dispositivo movel (referencia iPhone 16), permitindo decisoes de configuracao baseadas na experiencia real do usuario final. Layout colapsa adequadamente em telas menores.

## Contexto Arquitetural

- Layout side-by-side da F2-01 como base
- Frame de celular envolve o preview (PreviewSection / LandingPageView)
- Breakpoint segue padroes MUI (xs, sm, md, lg) ou equivalente

## Definition of Done do Epico
- [ ] Frame visual de celular aplicado ao preview
- [ ] Viewport do preview ~390px
- [ ] Tratamento de breakpoint implementado
- [ ] Layout colapsa para empilhado em viewports menores

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Aplicar frame visual de celular e viewport 390px | Frame de celular envolvendo preview; largura 390px | 3 | todo | [ISSUE-F2-02-001-Frame-Celular-390px.md](./issues/ISSUE-F2-02-001-Frame-Celular-390px.md) |
| ISSUE-F2-02-002 | Tratamento de breakpoint para viewports menores | Colapso do layout em telas pequenas | 2 | todo | [ISSUE-F2-02-002-Breakpoint-Viewports-Menores.md](./issues/ISSUE-F2-02-002-Breakpoint-Viewports-Menores.md) |

## Artifact Minimo do Epico

- Preview com frame de celular e viewport 390px
- Layout responsivo com breakpoint

## Dependencias
- [Intake](../../INTAKE-LP-PREVIEW.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [Fase](./F2_LP-PREVIEW_EPICS.md)
- [EPIC-F2-01](./EPIC-F2-01-Layout-Side-by-Side.md) — layout base
