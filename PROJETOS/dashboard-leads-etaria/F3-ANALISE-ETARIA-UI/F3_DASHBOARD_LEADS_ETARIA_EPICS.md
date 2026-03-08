---
doc_id: "F3_DASHBOARD_LEADS_ETARIA_EPICS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# Epicos - DASHBOARD-LEADS-ETARIA / F3 - ANALISE-ETARIA-UI

## Objetivo da Fase

Implementar a pagina completa da analise etaria no frontend, incluindo consumo da API, KPI cards, grafico, tabela, painel consolidado, filtros, banners de cobertura BB e tratamento completo dos estados da interface.

## Gate de Saida da Fase

A pagina `/dashboard/leads/analise-etaria` renderiza com dados reais da API, permite filtrar por evento e periodo, evidencia cobertura BB e trata loading, empty e error sem regressao visual.

## Gate de Auditoria da Fase

- estado_do_gate: `not_ready`
- ultima_auditoria: `nenhuma`
- veredito_atual: `n-a`
- relatorio_mais_recente: `n-a`
- log_do_projeto: [AUDIT-LOG](../AUDIT-LOG.md)
- convencao_de_relatorios: [README](./auditorias/README.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Dados e Visualizacoes da Analise Etaria | Implementar consumo da API, KPI cards, grafico, tabela, painel consolidado e filtros. | F2 concluida | active | [EPIC-F3-01-DADOS-E-VISUALIZACOES.md](./EPIC-F3-01-DADOS-E-VISUALIZACOES.md) |
| EPIC-F3-02 | Cobertura BB, Estados e Qualidade | Implementar banners de cobertura BB, skeletons, estados de erro/vazio e tooltips interpretativos. | EPIC-F3-01 | todo | [EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md](./EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: depende da fase F2 concluida
- `EPIC-F3-02`: depende de `EPIC-F3-01`

## Escopo desta Fase

### Dentro

- espelhar os tipos do backend no frontend e consumir a API tipada
- montar KPI cards, painel consolidado, grafico e tabela de eventos
- implementar filtros de periodo e evento com sincronizacao de URL
- implementar banners de cobertura BB e tooltips interpretativos
- tratar loading com skeletons, empty com mensagem e error com retry

### Fora

- exportacao para Excel ou PDF
- permissionamento granular por dashboard
- dashboards futuros alem da analise etaria

## Definition of Done da Fase

- [ ] pagina `/dashboard/leads/analise-etaria` renderiza com dados reais da API
- [ ] KPI cards exibem base total, clientes BB, faixa dominante e eventos no filtro
- [ ] grafico de barras empilhadas exibe distribuicao etaria por evento
- [ ] tabela de eventos exibe e ordena as colunas definidas no PRD
- [ ] painel consolidado mostra Top 3, media, mediana e concentracao Top 3
- [ ] filtros de periodo e evento funcionam e refletem a URL
- [ ] banner de cobertura BB aparece conforme os thresholds definidos
- [ ] estados loading, empty e error estao cobertos
- [ ] tooltips interpretativos para media, mediana, faixa dominante e cobertura BB estao acessiveis
- [ ] responsividade validada em desktop e mobile
- [ ] gate de auditoria preparado para futura rodada em `auditorias/`

## Navegacao Rapida

- [Intake](../INTAKE-DASHBOARD-LEADS-ETARIA.md)
- [PRD](../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Audit Log](../AUDIT-LOG.md)
- [Epic F3-01](./EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Epic F3-02](./EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md)
- `[[../INTAKE-DASHBOARD-LEADS-ETARIA]]`
- `[[../PRD-DASHBOARD-LEADS-ETARIA]]`
- `[[./EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[./EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE]]`
