---
doc_id: "F3_DASHBOARD_LEADS_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - DASHBOARD-LEADS / F3 - PARIDADE DOS CONSUMIDORES ANALITICOS

## Objetivo da Fase

Consolidar os consumidores analiticos priorizados sobre a semantica canonica, preservando payloads e filtros atuais.

## Gate de Saida da Fase

Os endpoints `/dashboard/leads/analise-etaria`, `/dashboard/leads` e `/dashboard/leads/relatorio` usam a semantica canonica aprovada e o frontend segue sem regressao funcional.

## Gate de Auditoria da Fase

- estado_do_gate: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `nao_aplicavel`
- log_do_projeto: [AUDIT-LOG](../../AUDIT-LOG.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Paridade da analise etaria | Consolidar a analise etaria no caminho canonico e provar que o contrato atual nao regrediu. | F2 concluida | todo | [EPIC-F3-01-PARIDADE-DA-ANALISE-ETARIA.md](./EPIC-F3-01-PARIDADE-DA-ANALISE-ETARIA.md) |
| EPIC-F3-02 | Consolidacao dos endpoints agregados de leads | Fechar `/dashboard/leads` e `/dashboard/leads/relatorio` sobre a mesma semantica canonica. | F2 concluida | todo | [EPIC-F3-02-CONSOLIDACAO-DOS-ENDPOINTS-AGREGADOS-DE-LEADS.md](./EPIC-F3-02-CONSOLIDACAO-DOS-ENDPOINTS-AGREGADOS-DE-LEADS.md) |
| EPIC-F3-03 | Contrato frontend e smoke de nao regressao | Travar os consumidores React sobre os contratos atuais sem redesenho ou mudanca de UX. | EPIC-F3-01, EPIC-F3-02 | todo | [EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md](./EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: F2 concluida
- `EPIC-F3-02`: F2 concluida
- `EPIC-F3-03`: EPIC-F3-01, EPIC-F3-02

## Escopo desta Fase

### Dentro

- consolidar a analise etaria no caminho canonico
- validar paridade e nao regressao de contrato
- consolidar `/dashboard/leads` e rankings
- consolidar `/dashboard/leads/relatorio`
- travar consumidores frontend e smoke de nao regressao

### Fora

- mudanca de UX ou payload frontend
- desativacao final de heuristicas residuais

## Definition of Done da Fase

- [ ] analise etaria usa a semantica canonica acordada no projeto
- [ ] endpoints agregados de leads mantem filtros e payloads atuais
- [ ] consumidores frontend seguem sem regressao funcional

## Navegacao Rapida

- [Intake](../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Audit Log](../../AUDIT-LOG.md)
- [EPIC-F3-01](./EPIC-F3-01-PARIDADE-DA-ANALISE-ETARIA.md)
- [EPIC-F3-02](./EPIC-F3-02-CONSOLIDACAO-DOS-ENDPOINTS-AGREGADOS-DE-LEADS.md)
- [EPIC-F3-03](./EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md)
