---
doc_id: "PHASE-F3-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# F3 Experiencia Dashboard - Epicos

## Objetivo da Fase

Materializar a navegacao do portfolio de dashboards e a pagina de analise etaria por evento com KPIs, tabela, grafico e estados de interface definidos no PRD.

## Gate de Saida da Fase

`/dashboard` exibe cards ativos e "Em breve", `/dashboard/leads/analise-etaria` esta protegida por autenticacao, carrega dados reais do endpoint novo e cobre carregando, sem dados, erro de API e banners de cobertura BB.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F3-01` | Manifesto e Navegacao Dashboard | Criar o manifesto de dashboards, a home do portfolio e a reserva de rotas futuras sem mexer no layout raiz a cada nova analise. | `todo` | [EPIC-F3-01-MANIFESTO-E-NAVEGACAO-DASHBOARD.md](./EPIC-F3-01-MANIFESTO-E-NAVEGACAO-DASHBOARD.md) |
| `EPIC-F3-02` | Pagina Analise Etaria | Implementar a pagina principal com filtros, painel consolidado, tabela por evento e visualizacao da distribuicao etaria. | `todo` | [EPIC-F3-02-PAGINA-ANALISE-ETARIA.md](./EPIC-F3-02-PAGINA-ANALISE-ETARIA.md) |
| `EPIC-F3-03` | Banners e Estados de Interface | Cobrir loading, empty state, erro com retry, dados parciais e avisos amarelo/vermelho de cobertura BB. | `todo` | [EPIC-F3-03-BANNERS-E-ESTADOS-DE-INTERFACE.md](./EPIC-F3-03-BANNERS-E-ESTADOS-DE-INTERFACE.md) |

## Escopo desta Entrega

Inclui manifesto configuravel, Home do dashboard, rota da analise etaria, consumo do endpoint, componentes visuais centrais e estados previstos pelo PRD. Exclui dashboards futuros fora do escopo v1.0 e exportacao para Excel/PDF.
