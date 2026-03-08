---
doc_id: "ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-01-001 - Criar FullPageBackground

## User Story

Como participante de evento, quero que a landing page tenha um fundo tematico que preencha toda a tela para sentir o contexto emocional do evento sem precisar de imagens ou textos explicativos.

## Contexto Tecnico

O componente `FullPageBackground` e um wrapper que aplica o gradiente do template e posiciona o overlay grafico como layer fixa (z-index 0). Usa os tokens ja fornecidos por `buildLandingTheme(data)` para calcular o `background` CSS. O gradiente e especifico por template (corporativo, esporte_convencional, etc.) conforme PRD secao 05.

## Plano TDD

- Red: renderizar landing page sem FullPageBackground — fundo e branco padrao do browser.
- Green: criar FullPageBackground com gradiente do template aplicado ao wrapper externo, cobrindo 100vw × 100vh.
- Refactor: extrair os valores de gradiente para constantes derivadas dos tokens do tema; garantir que o overlay grafico (ISSUE-F1-01-002) pode ser encaixado dentro do wrapper.

## Criterios de Aceitacao

- Given um template `corporativo`, When a landing carrega, Then o fundo exibe `linear-gradient(135deg, #1A237E 0%, #3333BD 60%, #465EFF 100%)` cobrindo 100vw × 100vh
- Given um template `esporte_radical`, When a landing carrega, Then o fundo exibe `linear-gradient(145deg, #3333BD 0%, #FF6E91 55%, #FCFC30 100%)`
- Given qualquer template, When a landing carrega, Then nao ha gap de cor padrao do browser entre o fundo e as bordas da viewport
- Given o componente FullPageBackground, When inspecionado no DOM, Then nenhuma tag `<img>` e gerada para o fundo

## Definition of Done da Issue

- [x] componente FullPageBackground criado em `frontend/src/components/landing/`
- [x] gradiente correto para os 7 templates conforme PRD secao 05
- [x] fundo preenche 100vw × 100vh sem gap
- [x] nenhuma imagem externa carregada para o fundo

## Tarefas Decupadas

- [x] T1: criar arquivo `FullPageBackground.tsx` com props para receber dados do tema
- [x] T2: mapear gradientes dos 7 templates a partir dos tokens de `buildLandingTheme`
- [x] T3: aplicar gradiente como `background` do wrapper com `position: fixed`, `inset: 0`
- [x] T4: exportar slot para children (card, footer) e para overlay grafico
- [x] T5: validar visualmente em pelo menos 3 templates (corporativo, esporte_radical, generico)

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/landingThemeBuilder.ts` (ou equivalente com `buildLandingTheme`)

## Artifact Minimo

- `frontend/src/components/landing/FullPageBackground.tsx`

## Orientacao de Refacao Pos-Entrega

- o componente criado nesta issue permanece valido e nao deve ser revertido
- a refacao orientada pelo paradigma atual deve atuar no contrato de estilo que o alimenta, removendo nomenclaturas e campos herdados de hero do arquivo `landingStyle.tsx`
- o objetivo da refacao nao e redesenhar o fundo, e sim alinhar nomes, tipos e props ao fato de que a landing agora e uma pagina form-only sem bloco hero

## Dependencias

- [Epic](../EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)

## Navegacao Rapida

- `[[../EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
