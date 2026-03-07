---
doc_id: "ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F1-03-001 - Remover Blocos Legados

## User Story

Como participante de evento, quero que a landing page nao exiba header com logo, hero image ou bloco "sobre o evento" para que eu veja apenas o formulario e preencha o mais rapido possivel.

## Contexto Tecnico

Os blocos a remover da view publica sao:
- Header com logo BB (elemento no topo da pagina)
- `HeroContextCard` (ou equivalente: nome da ativacao, descricao e hero image como secao separada)
- `<Box component="img" src={heroImageUrl}>` (hero image)
- `AboutEventCard` (quando/onde/link do evento)
- `BrandSummaryCard` (removido da view publica; mantido apenas em `isPreview` — fase F2)
- Grid de 2 colunas do hero

Os componentes nao devem ser deletados do codebase, apenas condicionados a `isPreview` ou desacoplados para reutilizacao futura. O titulo e subtitulo da ativacao ja foram migrados para dentro do FormCard (ISSUE-F1-02-001).

## Plano TDD

- Red: landing page atual exibe header, hero e about — participante precisa rolar para ver o formulario.
- Green: remover renderizacao condicional dos blocos na view publica (`!isPreview`); formulario aparece imediatamente.
- Refactor: limpar imports nao utilizados; mover blocos para renderizacao condicional `isPreview` para uso na fase F2.

## Criterios de Aceitacao

- Given a view publica (isPreview=false), When a landing carrega, Then nenhum header com logo BB e visivel
- Given a view publica, When a landing carrega, Then nenhuma hero image e renderizada
- Given a view publica, When a landing carrega, Then nenhum bloco "Sobre o evento" e visivel
- Given a view publica, When o DOM e inspecionado, Then nao ha tag `<img>` com `src` de hero image
- Given o codigo-fonte, When os blocos sao removidos da view publica, Then eles continuam disponiveis para uso condicional em `isPreview`

## Definition of Done da Issue

- [ ] Header com logo BB nao aparece na view publica
- [ ] HeroContextCard nao aparece na view publica
- [ ] AboutEventCard nao aparece na view publica
- [ ] hero image nao e carregada na view publica
- [ ] grid de 2 colunas substituido por Flexbox de coluna unica
- [ ] blocos preservados para uso condicional em isPreview

## Tarefas Decupadas

- [ ] T1: identificar todos os blocos legados em LandingPageView.tsx
- [ ] T2: envolver renderizacao do Header em condicional `isPreview`
- [ ] T3: envolver renderizacao do HeroContextCard em condicional `isPreview`
- [ ] T4: envolver renderizacao do AboutEventCard em condicional `isPreview`
- [ ] T5: remover hero image da view publica
- [ ] T6: substituir grid de 2 colunas por container de coluna unica

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`

## Artifact Minimo

- `frontend/src/components/landing/LandingPageView.tsx` (refatorado)

## Dependencias

- [Epic](../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
