---
doc_id: "EPIC-F3-01-DADOS-E-VISUALIZACOES.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F3-01 - Dados e Visualizacoes da Analise Etaria

## Objetivo

Implementar a página `LeadsAgeAnalysisPage` com consumo da API de análise etária,
KPI cards do painel consolidado, gráfico de barras empilhadas com distribuição etária
por evento, tabela de eventos com colunas configuráveis e painel consolidado com
Top 3, média e mediana. A página consome o endpoint criado na F1 e renderiza dentro
do `DashboardLayout` criado na F2.

## Resultado de Negocio Mensuravel

A pagina de analise etaria passa a exibir dados reais da API com visualizacoes e filtros acionaveis pelo usuario.

## Contexto Arquitetural

- Página em `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- Componentes em `frontend/src/components/dashboard/`
- API client via hook customizado (`useAgeAnalysis`) usando fetch/axios existente
- Endpoint: `GET /api/v1/dashboard/leads/analise-etaria`
- Resposta tipada: `AgeAnalysisResponse` (tipos espelhados do backend)
- Gráfico: avaliar biblioteca existente no projeto ou adicionar recharts

## Definition of Done do Epico

- [ ] Hook `useAgeAnalysis` consome a API e retorna dados tipados
- [ ] KPI cards renderizam base total, clientes BB e faixa dominante
- [ ] Gráfico de barras empilhadas renderiza distribuição etária por evento
- [ ] Tabela de eventos renderiza todas as colunas da seção 3.2 do PRD
- [ ] Painel consolidado exibe Top 3, média, mediana e concentração Top 3
- [ ] Filtros de período e evento funcionais
- [ ] Dados reais da API renderizados corretamente

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Criar tipos TypeScript e hook de consumo da API | Criar tipos TypeScript e hook de consumo da API | 3 | done | [ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md](./issues/ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md) |
| ISSUE-F3-01-002 | Implementar KPI Cards do painel consolidado | Implementar KPI Cards do painel consolidado | 3 | done | [ISSUE-F3-01-002-IMPLEMENTAR-KPI-CARDS-DO-PAINEL-CONSOLIDADO.md](./issues/ISSUE-F3-01-002-IMPLEMENTAR-KPI-CARDS-DO-PAINEL-CONSOLIDADO.md) |
| ISSUE-F3-01-003 | Implementar gráfico de barras empilhadas (distribuição etária) | Implementar gráfico de barras empilhadas (distribuição etária) | 5 | done | [ISSUE-F3-01-003-IMPLEMENTAR-GRAFICO-DE-BARRAS-EMPILHADAS-DISTRIBUICAO-ETARIA.md](./issues/ISSUE-F3-01-003-IMPLEMENTAR-GRAFICO-DE-BARRAS-EMPILHADAS-DISTRIBUICAO-ETARIA.md) |
| ISSUE-F3-01-004 | Implementar tabela de eventos com colunas configuráveis | Implementar tabela de eventos com colunas configuráveis | 5 | done | [ISSUE-F3-01-004-IMPLEMENTAR-TABELA-DE-EVENTOS-COM-COLUNAS-CONFIGURAVEIS.md](./issues/ISSUE-F3-01-004-IMPLEMENTAR-TABELA-DE-EVENTOS-COM-COLUNAS-CONFIGURAVEIS.md) |
| ISSUE-F3-01-005 | Implementar painel consolidado com Top 3, média e mediana | Implementar painel consolidado com Top 3, média e mediana | 3 | todo | [ISSUE-F3-01-005-IMPLEMENTAR-PAINEL-CONSOLIDADO-COM-TOP-3-MEDIA-E-MEDIANA.md](./issues/ISSUE-F3-01-005-IMPLEMENTAR-PAINEL-CONSOLIDADO-COM-TOP-3-MEDIA-E-MEDIANA.md) |
| ISSUE-F3-01-006 | Implementar filtros de período e evento | Implementar filtros de período e evento | 3 | todo | [ISSUE-F3-01-006-IMPLEMENTAR-FILTROS-DE-PERIODO-E-EVENTO.md](./issues/ISSUE-F3-01-006-IMPLEMENTAR-FILTROS-DE-PERIODO-E-EVENTO.md) |

## Artifact Minimo do Epico

- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/components/dashboard/KpiCard.tsx`
- `frontend/src/components/dashboard/EventsAgeTable.tsx`

## Dependencias

- [PRD](../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Fase](./F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Notas de Implementacao Globais

- Todos os componentes devem aceitar props tipadas — evitar `any`
- Formatação de números: usar `Intl.NumberFormat('pt-BR')` para consistência
- Percentuais sempre com 1 casa decimal e símbolo %
- Cores das faixas etárias devem ser consistentes entre gráfico, tabela e KPI cards

## Navegacao Rapida

- `[[./issues/ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API]]`
- `[[./issues/ISSUE-F3-01-002-IMPLEMENTAR-KPI-CARDS-DO-PAINEL-CONSOLIDADO]]`
- `[[./issues/ISSUE-F3-01-003-IMPLEMENTAR-GRAFICO-DE-BARRAS-EMPILHADAS-DISTRIBUICAO-ETARIA]]`
- `[[./issues/ISSUE-F3-01-004-IMPLEMENTAR-TABELA-DE-EVENTOS-COM-COLUNAS-CONFIGURAVEIS]]`
- `[[./issues/ISSUE-F3-01-005-IMPLEMENTAR-PAINEL-CONSOLIDADO-COM-TOP-3-MEDIA-E-MEDIANA]]`
- `[[./issues/ISSUE-F3-01-006-IMPLEMENTAR-FILTROS-DE-PERIODO-E-EVENTO]]`
- `[[../PRD-DASHBOARD-LEADS-ETARIA]]`
