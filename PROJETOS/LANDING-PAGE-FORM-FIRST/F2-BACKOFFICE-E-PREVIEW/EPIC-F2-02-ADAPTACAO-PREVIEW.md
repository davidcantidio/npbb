---
doc_id: "EPIC-F2-02-ADAPTACAO-PREVIEW.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F2-02 - Adaptacao do Modo Preview

## Objetivo

Adaptar o modo `isPreview` para exibir exatamente o novo layout form-only com badge "Preview" flutuante e sem blocos extras de metadados, marca ou checklist.

## Resultado de Negocio Mensuravel

O operador do backoffice ve exatamente o mesmo layout que o participante vera (form-only), com apenas um badge discreto de contexto operacional que nao polui a visualizacao final.

## Contexto Arquitetural

- `isPreview` e um boolean passado ao LandingPageView
- o preview deve renderizar o mesmo layout form-only (nao o layout antigo)
- elemento adicional do preview: badge "Preview" (canto superior direito, fora do card)
- o `template_override` deve controlar o fundo tematico no preview

## Definition of Done do Epico

- [x] preview exibe layout form-only (nao layout antigo)
- [x] badge "Preview" flutuante no canto superior direito
- [x] nenhum chip, checklist ou bloco de info de marca adicional aparece em preview
- [x] template_override muda fundo tematico em tempo de preview

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Adaptar Preview Form-Only | Adaptar preview para exibir layout form-only com badge Preview | 3 | done | [ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md](./issues/ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md) |
| ISSUE-F2-02-002 | Mover Chips para Secao Colapsavel | Mover chips mood/categoria para secao colapsavel dentro do card em preview | 3 | cancelled | [ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md](./issues/ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md) |

## Artifact Minimo do Epico

- `frontend/src/components/landing/LandingPageView.tsx` (modo preview adaptado)

## Dependencias

- [PRD](../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Fase](./F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY]]`
- `[[./issues/ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL]]`
- `[[../PRD-LANDING-PAGE-FORM-FIRST]]`
