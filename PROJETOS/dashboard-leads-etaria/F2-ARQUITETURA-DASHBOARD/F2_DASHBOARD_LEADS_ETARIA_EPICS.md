---
doc_id: "F2_DASHBOARD_LEADS_ETARIA_EPICS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# Epicos - DASHBOARD-LEADS-ETARIA / F2 - ARQUITETURA-DASHBOARD

## Objetivo da Fase

Implementar a arquitetura de navegacao do modulo Dashboard no frontend com manifesto declarativo, `DashboardLayout`, `DashboardHome` e roteamento protegido para a trilha `/dashboard`.

## Gate de Saida da Fase

O usuario autenticado acessa `/dashboard`, navega pela sidebar gerada a partir do manifesto e chega a `/dashboard/leads/analise-etaria` sem precisar alterar a arquitetura para adicionar novas analises.

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
| EPIC-F2-01 | Layout e Manifesto de Dashboards | Criar manifesto, `DashboardLayout`, `DashboardHome` e roteamento protegido para o modulo. | F1 concluida | done | [EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md](./EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: depende apenas da conclusao de F1

## Escopo desta Fase

### Dentro

- tipar manifesto de dashboards e entradas habilitadas/desabilitadas
- construir sidebar responsiva baseada no manifesto
- criar pagina raiz `DashboardHome` com cards clicaveis e "Em breve"
- configurar rotas `/dashboard/*` com protecao de autenticacao
- adicionar ponto de entrada do dashboard ao menu principal

### Fora

- implementacao das visualizacoes da analise etaria
- banners de cobertura BB e estados loading/empty/error
- dashboards futuros alem da trilha reservada no manifesto

## Definition of Done da Fase

- [x] manifesto de dashboards definido com ao menos uma entrada ativa e entradas futuras desabilitadas
- [x] `DashboardLayout` renderiza sidebar funcional baseada no manifesto
- [x] `DashboardHome` exibe cards em grid responsivo
- [x] cards desabilitados aparecem como "Em breve" e nao sao clicaveis
- [x] rotas `/dashboard` e `/dashboard/leads/analise-etaria` estao protegidas por autenticacao
- [x] a inclusao de uma nova entrada no manifesto rende um novo card sem alterar o layout
- [x] responsividade validada em desktop e mobile
- [x] gate de auditoria preparado para futura rodada em `auditorias/`

## Navegacao Rapida

- [Intake](../INTAKE-DASHBOARD-LEADS-ETARIA.md)
- [PRD](../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Audit Log](../AUDIT-LOG.md)
- [Epic F2-01](./EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md)
- `[[../INTAKE-DASHBOARD-LEADS-ETARIA]]`
- `[[../PRD-DASHBOARD-LEADS-ETARIA]]`
- `[[./EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS]]`
