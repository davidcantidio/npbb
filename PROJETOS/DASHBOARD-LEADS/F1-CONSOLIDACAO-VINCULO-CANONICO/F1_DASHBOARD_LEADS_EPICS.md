---
doc_id: "F1_DASHBOARD_LEADS_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - DASHBOARD-LEADS / F1 - CONSOLIDACAO DO VINCULO CANONICO

## Objetivo da Fase

Estabilizar a baseline do vinculo canonico `LeadEvento`, fechar a migration ausente e garantir escrita consistente nos fluxos publico, pipeline e ETL.

## Gate de Saida da Fase

A aplicacao sobe sem ImportError, a persistencia `lead_evento` esta versionada e os writers principais garantem `LeadEvento` sem quebrar contratos externos.

## Gate de Auditoria da Fase

- estado_do_gate: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `nao_aplicavel`
- log_do_projeto: [AUDIT-LOG](../../AUDIT-LOG.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Baseline de modelo, import e migration | Fechar a fundacao estrutural de `LeadEvento`, incluindo surface de import e migration versionada. | Intake, PRD, Fase atual | todo | [EPIC-F1-01-BASELINE-DE-MODELO-IMPORT-E-MIGRATION.md](./EPIC-F1-01-BASELINE-DE-MODELO-IMPORT-E-MIGRATION.md) |
| EPIC-F1-02 | Dual-write no fluxo publico e ativacao | Garantir `LeadEvento` nos caminhos de landing e submit publico, preservando `AtivacaoLead` como contexto de conversao. | EPIC-F1-01 | active | [EPIC-F1-02-DUAL-WRITE-NO-FLUXO-PUBLICO-E-ATIVACAO.md](./EPIC-F1-02-DUAL-WRITE-NO-FLUXO-PUBLICO-E-ATIVACAO.md) |
| EPIC-F1-03 | Dual-write em pipeline e ETL/importacao | Garantir `LeadEvento` nos caminhos batch e de ETL/importacao, com resolucao deterministica quando o evento vier apenas por nome. | EPIC-F1-01 | todo | [EPIC-F1-03-DUAL-WRITE-EM-PIPELINE-E-ETL-IMPORTACAO.md](./EPIC-F1-03-DUAL-WRITE-EM-PIPELINE-E-ETL-IMPORTACAO.md) |
| EPIC-F1-04 | Cobertura executavel e invariantes do vinculo | Alinhar fixtures e suites de regressao ao modelo canonico para que a baseline futura seja auditavel. | EPIC-F1-02, EPIC-F1-03 | todo | [EPIC-F1-04-COBERTURA-EXECUTAVEL-E-INVARIANTES-DO-VINCULO.md](./EPIC-F1-04-COBERTURA-EXECUTAVEL-E-INVARIANTES-DO-VINCULO.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: Intake, PRD, Fase atual
- `EPIC-F1-02`: EPIC-F1-01
- `EPIC-F1-03`: EPIC-F1-01
- `EPIC-F1-04`: EPIC-F1-02, EPIC-F1-03

## Escopo desta Fase

### Dentro

- corrigir export e import de `LeadEvento` e `LeadEventoSourceKind`
- criar ou validar migration versionada de `lead_evento`
- consolidar dual-write no submit publico com e sem ativacao
- consolidar dual-write no pipeline Gold e no ETL por `evento_nome` deterministico
- alinhar fixtures e testes ao modelo canonico

### Fora

- retroprocessamento historico amplo
- mudanca de payload nos endpoints de dashboard
- desativacao de heuristicas remanescentes fora da fundacao

## Definition of Done da Fase

- [ ] aplicacao sobe sem `ImportError` ligado a `LeadEventoSourceKind`
- [ ] migration de `lead_evento` existe e esta vinculada ao historico Alembic
- [ ] submit publico cria ou assegura `LeadEvento` com e sem ativacao
- [ ] pipeline Gold cria ou assegura `LeadEvento` via `LeadBatch.evento_id`
- [ ] ETL por `evento_nome` cria vinculo apenas quando o match e unico
- [ ] suite alvo de dashboard coleta e executa sobre fixtures canonicas

## Navegacao Rapida

- [Intake](../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Audit Log](../../AUDIT-LOG.md)
- [EPIC-F1-01](./EPIC-F1-01-BASELINE-DE-MODELO-IMPORT-E-MIGRATION.md)
- [EPIC-F1-02](./EPIC-F1-02-DUAL-WRITE-NO-FLUXO-PUBLICO-E-ATIVACAO.md)
- [EPIC-F1-03](./EPIC-F1-03-DUAL-WRITE-EM-PIPELINE-E-ETL-IMPORTACAO.md)
- [EPIC-F1-04](./EPIC-F1-04-COBERTURA-EXECUTAVEL-E-INVARIANTES-DO-VINCULO.md)
