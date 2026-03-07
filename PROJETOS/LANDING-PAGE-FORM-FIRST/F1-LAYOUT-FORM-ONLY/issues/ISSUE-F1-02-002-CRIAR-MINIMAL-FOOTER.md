---
doc_id: "ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F1-02-002 - Criar MinimalFooter

## User Story

Como participante de evento, quero ver um rodape discreto com a identidade do Banco do Brasil e o link de politica de privacidade para saber que estou em um ambiente oficial sem que isso ocupe espaco visual desnecessario.

## Contexto Tecnico

O MinimalFooter substitui o `BrandFooter` atual. Exibe apenas texto: tagline *"Banco do Brasil. Pra tudo que voce imaginar."* e link para politica de privacidade. Nenhuma logo ou imagem. A cor do texto e adaptada ao fundo tematico conforme PRD secao 05 (valores de `rodape texto` por template).

## Plano TDD

- Red: landing page sem rodape apos remocao do BrandFooter — nenhuma tagline ou link presente.
- Green: criar MinimalFooter com tagline, link de politica, typography `caption`, cor adaptada ao tema.
- Refactor: parametrizar cor do texto por template; posicionar dentro do fluxo normal abaixo do card/GamificacaoBlock.

## Criterios de Aceitacao

- Given qualquer template, When a landing carrega, Then o rodape exibe "Banco do Brasil. Pra tudo que voce imaginar." como texto
- Given qualquer template, When a landing carrega, Then o link "Politica de privacidade e LGPD" esta presente e funcional
- Given o template `corporativo`, When o rodape renderiza, Then a cor do texto e `rgba(255, 255, 255, 0.75)`
- Given o template `evento_cultural`, When o rodape renderiza, Then a cor do texto e `rgba(51, 51, 189, 0.75)`
- Given qualquer template, When o rodape e inspecionado, Then nenhuma tag `<img>` ou `<svg>` de logo e encontrada

## Definition of Done da Issue

- [ ] componente MinimalFooter criado em `frontend/src/components/landing/`
- [ ] tagline BB presente como texto sem logo
- [ ] link de politica de privacidade funcional
- [ ] cor do texto adaptada por template conforme PRD
- [ ] typography `caption` aplicada

## Tarefas Decupadas

- [ ] T1: criar arquivo `MinimalFooter.tsx` com props para cor do texto e URL da politica
- [ ] T2: renderizar tagline BB com `Typography variant="caption"`
- [ ] T3: renderizar link de politica com `Typography variant="caption"` e `<a>` funcional
- [ ] T4: mapear cor do texto do rodape por template a partir dos tokens do tema
- [ ] T5: posicionar abaixo do card (ou GamificacaoBlock) dentro do fluxo normal

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/landingThemeBuilder.ts` (tokens de cor do rodape)

## Artifact Minimo

- `frontend/src/components/landing/MinimalFooter.tsx`

## Dependencias

- [Epic](../EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F1-02-CARD-FORMULARIO-E-RODAPE]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
