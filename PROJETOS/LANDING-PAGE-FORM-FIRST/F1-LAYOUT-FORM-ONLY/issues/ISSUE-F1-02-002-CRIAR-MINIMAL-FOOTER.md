---
doc_id: "ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
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

- [x] componente MinimalFooter criado em `frontend/src/components/landing/`
- [x] tagline BB presente como texto sem logo
- [x] link de politica de privacidade funcional
- [x] cor do texto adaptada por template conforme PRD
- [x] typography `caption` aplicada

## Tarefas Decupadas

- [x] T1: criar arquivo `MinimalFooter.tsx` com props para cor do texto e URL da politica
- [x] T2: renderizar tagline BB com `Typography variant="caption"`
- [x] T3: renderizar link de politica com `Typography variant="caption"` e `<a>` funcional
- [x] T4: mapear cor do texto do rodape por template a partir dos tokens do tema
- [x] T5: posicionar abaixo do card (ou GamificacaoBlock) dentro do fluxo normal

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/landingStyle.tsx` (tokens de cor do rodape)
- `frontend/src/components/landing/MinimalFooter.tsx`

## Artifact Minimo

- `frontend/src/components/landing/MinimalFooter.tsx`

## Orientacao de Refacao Pos-Entrega

- o `MinimalFooter` permanece valido no paradigma atual e nao deve recuperar nenhum elemento de marca legado
- a refacao desta issue deve manter o rodape como superficie minima, recebendo apenas `tagline`, `privacyPolicyUrl` e cor efetivamente usada
- qualquer contrato compartilhado que ainda carregue semantica do layout antigo deve ser removido, sem alterar a composicao final do footer

## Dependencias

- [Epic](../EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)

## Navegacao Rapida

- `[[../EPIC-F1-02-CARD-FORMULARIO-E-RODAPE]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
