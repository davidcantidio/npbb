---
doc_id: "EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F1-02 - Card do Formulario e Rodape Minimo

## Objetivo

Criar o componente `FormCard` (card centralizado com o formulario) e o componente `MinimalFooter` (tagline BB + link de politica sem logo), que sao os dois elementos de primeiro plano do novo layout form-only.

## Resultado de Negocio Mensuravel

O card do formulario aparece above the fold em 375px × 667px sem scroll, centralizado em todos os breakpoints, com titulo derivado da ativacao, campos, LGPD e CTA. O rodape exibe apenas texto com link funcional.

## Contexto Arquitetural

- o FormCard encapsula: titulo (`ativacao.nome ?? evento.nome`), subtitulo opcional, callout `mensagem_qrcode`, campos do formulario, checkbox LGPD e botao CTA
- tokens de background, border e sombra do card sao derivados do template via `getLayoutVisualSpec`
- o MinimalFooter substitui o `BrandFooter` atual
- a cor do texto do rodape e adaptada ao fundo tematico (legivel sobre gradiente)
- referencia: PRD secoes 02.4 (Card) e RF-05, RF-06

## Definition of Done do Epico

- [x] FormCard renderiza titulo, subtitulo, callout, campos, LGPD e CTA
- [x] FormCard centralizado horizontal e verticalmente com Flexbox
- [x] FormCard responsivo: 92vw em mobile, max 480px em tablet, max 520px em desktop
- [x] FormCard com borderRadius 24px, elevacao e fundo branco/semitransparente conforme template
- [x] MinimalFooter exibe tagline BB e link de politica funcional
- [x] MinimalFooter sem logo ou imagem

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Criar FormCard | Implementar o card centralizado do formulario com tokens do tema | 5 | done | [ISSUE-F1-02-001-CRIAR-FORMCARD.md](./issues/ISSUE-F1-02-001-CRIAR-FORMCARD.md) |
| ISSUE-F1-02-002 | Criar MinimalFooter | Implementar o rodape minimo com tagline BB e link de politica | 2 | done | [ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER.md](./issues/ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER.md) |

## Artifact Minimo do Epico

- `frontend/src/components/landing/FormCard.tsx`
- `frontend/src/components/landing/MinimalFooter.tsx`

## Refacao Residual Apos a Entrega

- FormCard e MinimalFooter estao corretos como composicao final da landing
- o alinhamento restante desta etapa e reduzir o acoplamento desses componentes ao contrato visual herdado do layout antigo
- a refacao deve extrair um contrato minimo de tokens consumidos pelo form-only, evitando que `FormCard` continue recebendo um `layout` com campos ligados a hero ou grid legado

## Dependencias

- [PRD](../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Fase](./F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F1-02-001-CRIAR-FORMCARD]]`
- `[[./issues/ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER]]`
- `[[../PRD-LANDING-PAGE-FORM-FIRST]]`
