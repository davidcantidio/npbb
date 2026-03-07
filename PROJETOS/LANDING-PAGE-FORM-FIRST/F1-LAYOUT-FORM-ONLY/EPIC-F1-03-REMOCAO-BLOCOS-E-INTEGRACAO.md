---
doc_id: "EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# EPIC-F1-03 - Remocao de Blocos Legados e Integracao

## Objetivo

Remover da view publica os blocos legados (Header, HeroContextCard, AboutEventCard), reposicionar o GamificacaoBlock abaixo do FormCard, e integrar todos os componentes novos (FullPageBackground + FormCard + MinimalFooter) no LandingPageView.tsx.

## Resultado de Negocio Mensuravel

A view publica da landing page exibe apenas o fundo tematico, o card do formulario, o GamificacaoBlock (se aplicavel) e o rodape minimo. Nenhum bloco legado aparece. O fluxo de submit, reset e gamificacao funciona sem regressao.

## Contexto Arquitetural

- `LandingPageView.tsx` e o ponto de montagem que precisa ser reestruturado
- o grid de 2 colunas atual deve ser substituido por Flexbox de coluna unica
- os componentes removidos da view publica podem ser preservados para uso em `isPreview` (fase F2)
- os handlers `handleSubmitSuccess`, `handleReset`, `handleGamificacaoComplete` devem ser mantidos intactos
- referencia: PRD secao 07 (Impacto no Codigo)

## Definition of Done do Epico

- [ ] Header com logo BB removido da view publica
- [ ] HeroContextCard removido da view publica
- [ ] AboutEventCard removido da view publica
- [ ] GamificacaoBlock posicionado abaixo do FormCard com mesma largura maxima
- [ ] LandingPageView integra FullPageBackground + FormCard + GamificacaoBlock + MinimalFooter
- [ ] fluxo de submit, reset e gamificacao funcional sem regressao
- [ ] layout responsivo em 375px, 768px e 1280px

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-03-001 | Remover Blocos Legados | Remover Header, HeroContextCard e AboutEventCard da view publica | 3 | todo | [ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md](./issues/ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md) |
| ISSUE-F1-03-002 | Reposicionar GamificacaoBlock | Mover GamificacaoBlock para abaixo do FormCard com mesma largura maxima | 3 | todo | [ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md](./issues/ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md) |
| ISSUE-F1-03-003 | Integrar Layout Form-Only | Montar o LandingPageView com os componentes novos em Flexbox de coluna unica | 3 | todo | [ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md](./issues/ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md) |

## Artifact Minimo do Epico

- `frontend/src/components/landing/LandingPageView.tsx` (refatorado)

## Dependencias

- [PRD](../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Fase](./F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Epic F1-01](./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md)
- [Epic F1-02](./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS]]`
- `[[./issues/ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK]]`
- `[[./issues/ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY]]`
- `[[../PRD-LANDING-FORM-ONLY-v1.0]]`
