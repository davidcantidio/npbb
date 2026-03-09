---
doc_id: "EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F1-03 - Remocao de Blocos Legados e Integracao

## Objetivo

Remover da view publica os blocos legados (Header, HeroContextCard, AboutEventCard), reposicionar o GamificacaoBlock abaixo do FormCard, e integrar todos os componentes novos (FullPageBackground + FormCard + MinimalFooter) no LandingPageView.tsx.

## Resultado de Negocio Mensuravel

A view publica da landing page exibe apenas o fundo tematico, o card do formulario, o GamificacaoBlock (se aplicavel) e o rodape minimo. Nenhum bloco legado aparece. O fluxo de submit, reset e gamificacao funciona sem regressao.

## Contexto Arquitetural

- `LandingPageView.tsx` e o ponto de montagem que precisa ser reestruturado
- o grid de 2 colunas atual deve ser substituido por Flexbox de coluna unica
- os componentes removidos da view publica nao sao preservados no runtime; o preview passa a usar a mesma composicao form-only
- os handlers `handleSubmitSuccess`, `handleReset`, `handleGamificacaoComplete` devem ser mantidos intactos
- referencia: PRD secao 07 (Impacto no Codigo)

## Definition of Done do Epico

- [x] Header com logo BB removido da view publica
- [x] HeroContextCard removido da view publica
- [x] AboutEventCard removido da view publica
- [x] GamificacaoBlock posicionado abaixo do FormCard com mesma largura maxima
- [x] LandingPageView integra FullPageBackground + FormCard + GamificacaoBlock + MinimalFooter
- [x] fluxo de submit, reset e gamificacao funcional sem regressao
- [x] layout responsivo em 375px, 768px e 1280px

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-03-001 | Remover Blocos Legados | Remover Header, HeroContextCard e AboutEventCard da view publica | 3 | done | [ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md](./issues/ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md) |
| ISSUE-F1-03-002 | Reposicionar GamificacaoBlock | Mover GamificacaoBlock para abaixo do FormCard com mesma largura maxima | 3 | done | [ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md](./issues/ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md) |
| ISSUE-F1-03-003 | Integrar Layout Form-Only | Montar o LandingPageView com os componentes novos em Flexbox de coluna unica | 3 | done | [ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md](./issues/ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md) |
| ISSUE-F1-03-004 | Alinhar Cor de Rodape `esporte_radical` ao Contrato | Corrigir divergencia de contrato entre implementacao, PRD e teste na cor do rodape | 2 | done | [ISSUE-F1-03-004-ALINHAR-COR-RODAPE-ESPORTE-RADICAL-E-CONTRATO.md](./issues/ISSUE-F1-03-004-ALINHAR-COR-RODAPE-ESPORTE-RADICAL-E-CONTRATO.md) |

## Artifact Minimo do Epico

- `frontend/src/components/landing/LandingPageView.tsx` (refatorado)

## Refacao Residual Apos a Entrega

- a integracao final removeu o runtime legado, mas ainda consome nomes herdados de hero em partes do contrato visual compartilhado
- a proxima refacao desta etapa deve alinhar `LandingPageView`, `FormCard` e `landingStyle.tsx` ao paradigma form-only sem reintroduzir qualquer bloco legado
- o criterio de encerramento tecnico desta limpeza e: nenhum componente ativo da landing depender de campo, prop ou tipo cuja semantica ainda descreva hero, grid lateral ou card de contexto removido

## Follow-up de Auditoria F1-R01

- gate liberado para F1 após conclusão da issue bloqueante `ISSUE-F1-03-004`
- origem do follow-up: `auditorias/RELATORIO-AUDITORIA-F1-R01.md`

## Dependencias

- [PRD](../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Fase](./F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Epic F1-01](./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md)
- [Epic F1-02](./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS]]`
- `[[./issues/ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK]]`
- `[[./issues/ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY]]`
- `[[./issues/ISSUE-F1-03-004-ALINHAR-COR-RODAPE-ESPORTE-RADICAL-E-CONTRATO]]`
- `[[../PRD-LANDING-PAGE-FORM-FIRST]]`
