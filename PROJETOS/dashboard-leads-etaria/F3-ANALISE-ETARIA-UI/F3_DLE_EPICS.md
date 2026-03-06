# Épicos — Dashboard Leads Etária / F3 — Análise Etária UI
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F3
**prd:** ../PRD_Dashboard_Portfolio.md
**status:** aprovado

---
## Objetivo da Fase
Implementar a página completa de análise etária no frontend: consumo da API, KPI cards
do painel consolidado, gráfico de barras empilhadas por evento, tabela de eventos com
colunas configuráveis, painel consolidado com Top 3/média/mediana, banners de cobertura
BB e tratamento completo de estados da interface (loading, empty, error).

Ao final da fase, o usuário pode acessar `/dashboard/leads/analise-etaria`, ver a
distribuição etária por evento e consolidada, identificar eventos com dados BB
ausentes e interagir com filtros e ordenação.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Dados e Visualizações da Análise Etária | Implementar consumo da API, KPI cards, gráfico de barras e tabela de eventos. | F2 (layout pronto) | 🔲 | `EPIC-F3-01-DADOS-E-VISUALIZACOES.md` |
| EPIC-F3-02 | Cobertura BB, Estados e Qualidade | Implementar banners de cobertura BB, estados da interface e tooltips interpretativos. | EPIC-F3-01 | 🔲 | `EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md` |

## Dependências entre Épicos
`EPIC-F3-01` → `EPIC-F3-02`

## Definition of Done da Fase
- [ ] Página `/dashboard/leads/analise-etaria` renderiza com dados reais da API
- [ ] KPI cards exibem base total, clientes BB (com indicador de cobertura), faixa dominante
- [ ] Gráfico de barras empilhadas exibe distribuição etária por evento
- [ ] Tabela de eventos com colunas configuráveis, ordenável por volume/percentual
- [ ] Painel consolidado com Top 3, média, mediana e concentração Top 3
- [ ] Filtros de período e evento funcionais
- [ ] Banner de dados BB ausentes exibido conforme threshold de cobertura
- [ ] Estados de loading (skeleton), empty e error tratados corretamente
- [ ] Tooltips interpretativos para faixa dominante, média e mediana
- [ ] Responsividade testada em desktop e mobile

## Notas e Restrições
- Gráfico de barras: usar biblioteca já disponível no projeto (recharts, Chart.js ou similar)
  ou adicionar dependência leve se nenhuma existir
- Não implementar exportação para Excel/PDF nesta fase
- Não implementar permissionamento granular por dashboard
