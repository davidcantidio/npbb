---
doc_id: "EPIC-F2-02-ADAPTACAO-PREVIEW.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# EPIC-F2-02 - Adaptacao do Modo Preview

## Objetivo

Adaptar o modo `isPreview` para exibir o novo layout form-only com badge "Preview" flutuante, chips mood/categoria em secao colapsavel e bloco de info de marca abaixo do GamificacaoBlock.

## Resultado de Negocio Mensuravel

O operador do backoffice ve exatamente o mesmo layout que o participante vera (form-only), com indicadores adicionais de contexto operacional (badge, chips, info de marca) que nao poluem a view publica.

## Contexto Arquitetural

- `isPreview` e um boolean passado ao LandingPageView
- o preview deve renderizar o mesmo layout form-only (nao o layout antigo)
- elementos adicionais do preview: badge "Preview" (canto superior direito, fora do card), chips mood/categoria (secao colapsavel dentro do card), bloco de marca (abaixo do GamificacaoBlock)
- o `template_override` deve controlar o fundo tematico no preview

## Definition of Done do Epico

- [ ] preview exibe layout form-only (nao layout antigo)
- [ ] badge "Preview" flutuante no canto superior direito
- [ ] chips mood/categoria em secao colapsavel dentro do card (apenas em preview)
- [ ] bloco de info de marca abaixo do GamificacaoBlock (apenas em preview)
- [ ] template_override muda fundo tematico em tempo de preview

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Adaptar Preview Form-Only | Adaptar preview para exibir layout form-only com badge Preview | 3 | todo | [ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md](./issues/ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md) |
| ISSUE-F2-02-002 | Mover Chips para Secao Colapsavel | Mover chips mood/categoria para secao colapsavel dentro do card em preview | 3 | todo | [ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md](./issues/ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md) |

## Artifact Minimo do Epico

- `frontend/src/components/landing/LandingPageView.tsx` (modo preview adaptado)

## Dependencias

- [PRD](../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Fase](./F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY]]`
- `[[./issues/ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL]]`
- `[[../PRD-LANDING-FORM-ONLY-v1.0]]`
