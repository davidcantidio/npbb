---
doc_id: "ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-01-002 - Adaptar renderGraphicOverlay

## User Story

Como participante de evento, quero que o grafismo do template (formas geometricas, particulas, grid) apareca como camada decorativa sobre o fundo da pagina para reforcar a identidade visual sem interferir no formulario.

## Contexto Tecnico

A funcao `renderGraphicOverlay(data)` ja gera o elemento SVG/React com o overlay grafico do template. Atualmente ela assume posicionamento dentro de um container hero. Precisa ser reposicionada como layer fixa dentro do `FullPageBackground`, com z-index entre o gradiente (z-index 0) e o card do formulario (z-index 1).

## Plano TDD

- Red: renderGraphicOverlay no container atual — posicionamento quebra quando removemos o hero.
- Green: reposicionar renderGraphicOverlay dentro do FullPageBackground como layer `position: fixed` com `inset: 0` e `pointer-events: none`.
- Refactor: verificar que a opacidade do overlay respeita os valores do PRD por template (8-20%) e que nao interfere com interacoes do formulario.

## Criterios de Aceitacao

- Given o template `corporativo`, When a landing carrega, Then o overlay exibe linhas retas com opacidade 8-12% sobre o gradiente
- Given o template `show_musical`, When a landing carrega, Then o overlay exibe particulas/brilhos com opacidade 20%
- Given qualquer template, When o usuario interage com o formulario, Then o overlay nao intercepta cliques (pointer-events: none)
- Given o FullPageBackground, When renderGraphicOverlay e chamado, Then o overlay e posicionado como layer fixa cobrindo a viewport inteira

## Definition of Done da Issue

- [x] renderGraphicOverlay funciona sem regressao visual dentro do FullPageBackground
- [x] overlay posicionado como layer fixa com pointer-events: none
- [x] opacidade do overlay respeita valores do PRD por template
- [x] nenhuma interacao com o formulario e bloqueada pelo overlay

## Tarefas Decupadas

- [x] T1: identificar como renderGraphicOverlay e chamado atualmente e qual container DOM assume
- [x] T2: mover a chamada de renderGraphicOverlay para dentro do FullPageBackground
- [x] T3: aplicar `position: fixed`, `inset: 0`, `pointer-events: none` ao container do overlay
- [x] T4: validar opacidade por template (corporativo 8-12%, show_musical 20%, etc.)
- [x] T5: testar que cliques no formulario nao sao interceptados pelo overlay

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/FullPageBackground.tsx` (criado na ISSUE-F1-01-001)
- `frontend/src/components/landing/landingThemeBuilder.ts` (ou equivalente com `renderGraphicOverlay`)

## Artifact Minimo

- `frontend/src/components/landing/FullPageBackground.tsx` (atualizado com overlay)

## Orientacao de Refacao Pos-Entrega

- a adaptacao do overlay esta correta e permanece como base do layout final
- a refacao desta etapa deve garantir que o overlay dependa apenas de semantica de pagina full-page, sem referencias conceituais a hero container no contrato visual compartilhado
- se houver limpeza de tipos em `landingStyle.tsx`, preservar o comportamento de `renderGraphicOverlay(data)` e sua camada fixa, alterando apenas nomes e campos mortos

## Dependencias

- [Epic](../EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Issue 001](./ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND.md)

## Navegacao Rapida

- `[[../EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER]]`
- `[[./ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
