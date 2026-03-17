---
doc_id: "F4_DASHBOARD_LEADS_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - DASHBOARD-LEADS / F4 - DESATIVACAO DO HEURISTICO E ENDURECIMENTO

## Objetivo da Fase

Remover residuos do caminho heuristico, fechar observabilidade, rollback e pacote de auditoria final da remediacao.

## Gate de Saida da Fase

Nao restam helpers/fallbacks fora do caminho oficial e o projeto possui runbook, metricas e evidencias suficientes para auditoria da fase.

## Gate de Auditoria da Fase

- estado_do_gate: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `nao_aplicavel`
- log_do_projeto: [AUDIT-LOG](../../AUDIT-LOG.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F4-01 | Retirada controlada do heuristico | Eliminar codigo residual de uniao heuristica que nao faca mais parte do caminho aprovado. | F3 concluida | todo | [EPIC-F4-01-RETIRADA-CONTROLADA-DO-HEURISTICO.md](./EPIC-F4-01-RETIRADA-CONTROLADA-DO-HEURISTICO.md) |
| EPIC-F4-02 | Observabilidade, rollback e auditoria final | Consolidar o pacote operacional final para auditoria da remediacao. | EPIC-F4-01 | todo | [EPIC-F4-02-OBSERVABILIDADE-ROLLBACK-E-AUDITORIA-FINAL.md](./EPIC-F4-02-OBSERVABILIDADE-ROLLBACK-E-AUDITORIA-FINAL.md) |

## Dependencias entre Epicos

- `EPIC-F4-01`: F3 concluida
- `EPIC-F4-02`: EPIC-F4-01

## Escopo desta Fase

### Dentro

- remover helpers e fallbacks residuais fora do caminho oficial
- consolidar rollback, metricas e evidencias finais de auditoria

### Fora

- mudanca de payload ou UX frontend
- novos writers ou readers fora do escopo da remediacao aprovada

## Definition of Done da Fase

- [ ] residuos heuristicas fora do caminho oficial removidos
- [ ] runbook de rollback documentado
- [ ] metricas e evidencias finais consolidadas para auditoria

## Navegacao Rapida

- [Intake](../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Audit Log](../../AUDIT-LOG.md)
- [EPIC-F4-01](./EPIC-F4-01-RETIRADA-CONTROLADA-DO-HEURISTICO.md)
- [EPIC-F4-02](./EPIC-F4-02-OBSERVABILIDADE-ROLLBACK-E-AUDITORIA-FINAL.md)
