---
doc_id: "F3_DL2_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
audit_gate: "not_ready"
---

# Epicos - DL2 / F3 - Convergencia dos dashboards agregados

## Objetivo da Fase

Alinhar dashboard agregado, rankings e relatorio sobre a mesma fonte de verdade, preservando o contrato consumido pelo frontend.

## Gate de Saida da Fase

`/dashboard/leads`, `/dashboard/leads/relatorio` e seus consumidores frontend ficam coerentes com a analise etaria para o mesmo evento.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/DL2/F3-CONVERGENCIA-DOS-DASHBOARDS-AGREGADOS/auditorias/RELATORIO-AUDITORIA-F3-R01.md`
- log_do_projeto: [PROJETOS/DL2/AUDIT-LOG.md](PROJETOS/DL2/AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F3-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F3-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F3-01 | Dashboard agregado e rankings coerentes por evento | Consolidar KPIs, series e rankings de `/dashboard/leads` sobre a mesma leitura canonica. | Feature 2 | F2 aprovada | todo | [EPIC-F3-01-DASHBOARD-AGREGADO-E-RANKINGS-COERENTES-POR-EVENTO.md](./EPIC-F3-01-DASHBOARD-AGREGADO-E-RANKINGS-COERENTES-POR-EVENTO.md) |
| EPIC-F3-02 | Relatorio agregado coerente por evento | Fechar `/dashboard/leads/relatorio` sobre a mesma semantica canonica dos demais consumidores priorizados. | Feature 2 | EPIC-F3-01 | todo | [EPIC-F3-02-RELATORIO-AGREGADO-COERENTE-POR-EVENTO.md](./EPIC-F3-02-RELATORIO-AGREGADO-COERENTE-POR-EVENTO.md) |
| EPIC-F3-03 | Contrato frontend e smoke de nao regressao | Travar os consumidores React sobre os contratos consolidados do backend sem redesenho de UX. | Feature 2 | EPIC-F3-01, EPIC-F3-02 | todo | [EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md](./EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: depende da conclusao de `F2`
- `EPIC-F3-02`: depende de `EPIC-F3-01`
- `EPIC-F3-03`: depende de `EPIC-F3-01` e `EPIC-F3-02`

## Escopo desta Fase

### Dentro
- consolidar `/dashboard/leads` sobre a mesma semantica da analise etaria
- consolidar `/dashboard/leads/relatorio` sobre a mesma base de leitura
- travar contratos frontend e smoke de nao regressao

### Fora
- backfill historico, reconciliacao e fallback operacional
- retirada do heuristico residual
- redesign visual dos dashboards

## Definition of Done da Fase
- [ ] contagens para o mesmo evento convergem entre as tres superficies priorizadas
- [ ] rankings, filtros e relatorio usam a semantica canonica acordada
- [ ] frontend segue sem regressao funcional e sem mudanca de payload
