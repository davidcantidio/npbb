---
doc_id: "SPRINT-F1-02.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# SPRINT-F1-02

## Objetivo da Sprint

Remover os blocos legados da view publica, reposicionar o GamificacaoBlock e integrar todos os componentes novos no LandingPageView. Ao final, a landing page funciona no novo layout form-only.

## Capacidade

- story_points_planejados: 9
- issues_planejadas: 3
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-03-001 | Remover Blocos Legados | 3 | done | [ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md](../issues/ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md) |
| ISSUE-F1-03-002 | Reposicionar GamificacaoBlock | 3 | done | [ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md](../issues/ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md) |
| ISSUE-F1-03-003 | Integrar Layout Form-Only | 3 | done | [ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md](../issues/ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md) |

## Riscos e Bloqueios

- remocao de blocos pode quebrar referencia de componentes internos — verificar imports
- integracao depende dos componentes da SPRINT-F1-01 estarem prontos e testados
- fluxo de gamificacao pode ter regressao no novo posicionamento

## Encerramento

- decisao: concluida
- observacoes: a landing publica foi consolidada no layout form-only com gamificacao reposicionada e runtime legado removido.

## Saldo de Refacao Identificado Depois da Entrega

- limpar nomes e tipos herdados de hero ainda usados na integracao final
- estreitar o contrato visual compartilhado entre `LandingPageView`, `FormCard` e `MinimalFooter`
- manter como proibicao explicita qualquer retorno de Header, HeroContextCard, AboutEventCard, BrandSummaryCard ou checklist operacional

## Navegacao Rapida

- [Epic F1-03](../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- `[[../issues/ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS]]`
- `[[../issues/ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK]]`
- `[[../issues/ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY]]`
