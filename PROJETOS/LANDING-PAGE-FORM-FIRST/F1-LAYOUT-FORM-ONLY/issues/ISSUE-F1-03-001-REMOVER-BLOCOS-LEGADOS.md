---
doc_id: "ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
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
- `BrandSummaryCard`
- Grid de 2 colunas do hero

Os componentes legados deixam de fazer parte do runtime da landing. O titulo e subtitulo da ativacao ja foram migrados para dentro do FormCard (ISSUE-F1-02-001).

## Plano TDD

- Red: landing page atual exibe header, hero e about — participante precisa rolar para ver o formulario.
- Green: remover renderizacao dos blocos legados; formulario aparece imediatamente.
- Refactor: limpar imports nao utilizados e remover codigo morto do layout antigo.

## Criterios de Aceitacao

- Given a view publica (isPreview=false), When a landing carrega, Then nenhum header com logo BB e visivel
- Given a view publica, When a landing carrega, Then nenhuma hero image e renderizada
- Given a view publica, When a landing carrega, Then nenhum bloco "Sobre o evento" e visivel
- Given a view publica, When o DOM e inspecionado, Then nao ha tag `<img>` com `src` de hero image
- Given o codigo-fonte, When os blocos sao removidos da landing, Then o runtime nao depende mais de nenhum componente legado

## Definition of Done da Issue

- [x] Header com logo BB nao aparece na view publica
- [x] HeroContextCard nao aparece na view publica
- [x] AboutEventCard nao aparece na view publica
- [x] hero image nao e carregada na view publica
- [x] grid de 2 colunas substituido por Flexbox de coluna unica
- [x] runtime legado removido da composicao principal

## Tarefas Decupadas

- [x] T1: identificar todos os blocos legados em LandingPageView.tsx
- [x] T2: remover o Header da composicao da landing
- [x] T3: remover HeroContextCard e hero image da composicao
- [x] T4: remover AboutEventCard e BrandSummaryCard
- [x] T5: garantir ausencia de hero image na view publica e no preview
- [x] T6: substituir grid de 2 colunas por container de coluna unica

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`

## Artifact Minimo

- `frontend/src/components/landing/LandingPageView.tsx` (refatorado)

## Dependencias

- [Epic](../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)

## Navegacao Rapida

- `[[../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
