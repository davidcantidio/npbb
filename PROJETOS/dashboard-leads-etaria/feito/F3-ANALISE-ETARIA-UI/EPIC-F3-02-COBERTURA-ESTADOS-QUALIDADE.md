---
doc_id: "EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F3-02 - Cobertura BB, Estados e Qualidade

## Objetivo

Implementar os banners de aviso de dados BB (amarelo e vermelho conforme threshold de
cobertura), tratamento completo dos estados da interface (loading com skeleton loaders,
empty, error com retry) e tooltips interpretativos para métricas que requerem
contextualização (média vs. mediana, faixa dominante).

## Resultado de Negocio Mensuravel

A interface passa a explicar a qualidade dos dados e a responder bem a loading, vazio e erro, sem esconder limitacoes do cruzamento BB.

## Contexto Arquitetural

- Componentes em `frontend/src/components/dashboard/`
- Lógica de cobertura BB vem do campo `cobertura_bb_pct` da resposta da API
- Thresholds: ≥ 80% (normal), 20–80% (amarelo), < 20% (vermelho)
- Estados de interface controlados pelo hook `useAgeAnalysis` (loading, error, data)
- Padrão de toast/notificação existente no projeto para erros

## Definition of Done do Epico

- [ ] Banner amarelo exibido quando cobertura BB entre 20% e 80%
- [ ] Banner vermelho exibido quando cobertura BB < 20%
- [ ] Sem banner quando cobertura ≥ 80%
- [ ] Skeleton loaders em KPI cards, gráfico e tabela durante loading
- [ ] Estado empty: "Nenhum lead encontrado para os filtros aplicados"
- [ ] Estado error: toast de erro com botão de retry
- [ ] Tooltips interpretativos para média, mediana e faixa dominante

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-02-001 | Implementar banners de aviso de dados BB | Implementar banners de aviso de dados BB | 3 | done | [ISSUE-F3-02-001-IMPLEMENTAR-BANNERS-DE-AVISO-DE-DADOS-BB.md](./issues/ISSUE-F3-02-001-IMPLEMENTAR-BANNERS-DE-AVISO-DE-DADOS-BB.md) |
| ISSUE-F3-02-002 | Implementar estados da interface (loading, empty, error) | Implementar estados da interface (loading, empty, error) | 3 | todo | [ISSUE-F3-02-002-IMPLEMENTAR-ESTADOS-DA-INTERFACE-LOADING-EMPTY-ERROR.md](./issues/ISSUE-F3-02-002-IMPLEMENTAR-ESTADOS-DA-INTERFACE-LOADING-EMPTY-ERROR.md) |
| ISSUE-F3-02-003 | Tooltips interpretativos e documentação visual | Tooltips interpretativos e documentação visual | 2 | done | [ISSUE-F3-02-003-TOOLTIPS-INTERPRETATIVOS-E-DOCUMENTACAO-VISUAL.md](./issues/ISSUE-F3-02-003-TOOLTIPS-INTERPRETATIVOS-E-DOCUMENTACAO-VISUAL.md) |
| ISSUE-F3-02-004 | Alinhar contratos de teste da tabela e KPIs | Reconciliar contrato de exibicao da tabela/KPIs com a suite de testes da analise etaria apos hold F3-R01. | 2 | todo | [ISSUE-F3-02-004-ALINHAR-CONTRATOS-DE-TESTE-DA-TABELA-E-KPIS.md](./issues/ISSUE-F3-02-004-ALINHAR-CONTRATOS-DE-TESTE-DA-TABELA-E-KPIS.md) |

## Artifact Minimo do Epico

- `frontend/src/components/dashboard/CoverageBanner.tsx`
- `frontend/src/components/dashboard/KpiCardSkeleton.tsx`
- `frontend/src/components/dashboard/InfoTooltip.tsx`

## Dependencias

- [PRD](../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Fase](./F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Notas de Implementacao Globais

- Banners e estados devem ser testados com dados reais e cenários extremos
- Skeleton loaders devem ter dimensões próximas ao conteúdo real para evitar layout shift
- Cores dos banners: amarelo (#FEF3C7 bg / #92400E text) e vermelho (#FEE2E2 bg / #991B1B text)
— ajustar conforme sistema de cores do projeto

## Navegacao Rapida

- `[[./issues/ISSUE-F3-02-001-IMPLEMENTAR-BANNERS-DE-AVISO-DE-DADOS-BB]]`
- `[[./issues/ISSUE-F3-02-002-IMPLEMENTAR-ESTADOS-DA-INTERFACE-LOADING-EMPTY-ERROR]]`
- `[[./issues/ISSUE-F3-02-003-TOOLTIPS-INTERPRETATIVOS-E-DOCUMENTACAO-VISUAL]]`
- `[[./issues/ISSUE-F3-02-004-ALINHAR-CONTRATOS-DE-TESTE-DA-TABELA-E-KPIS]]`
- `[[../PRD-DASHBOARD-LEADS-ETARIA]]`
