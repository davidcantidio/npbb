---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups sempre que uma auditoria real de feature retornar
`hold`.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         ATIVOS-INGRESSOS
FEATURE_ID:      <resolver_na_ultima_auditoria_hold>
FEATURE_PATH:    <resolver_na_ultima_auditoria_hold>
RELATORIO_PATH:  <resolver_na_ultima_auditoria_hold>
AUDIT_LOG_PATH:  PROJETOS/ATIVOS-INGRESSOS/AUDIT-LOG.md
OBSERVACOES:     usar o ultimo relatorio `hold` realmente ativo
```

## Regra Local Adicional

- use este wrapper apenas quando houver um `hold` real aberto no projeto
- resolva feature e relatorio a partir do `AUDIT-LOG.md`, nunca de artefatos bootstrap legados
