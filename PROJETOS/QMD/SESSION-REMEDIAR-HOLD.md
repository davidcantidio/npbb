---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "QMD"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups de QMD somente quando existir uma auditoria `hold` real do projeto.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         QMD
FASE:            <resolver_na_ultima_auditoria_hold>
RELATORIO_PATH:  <resolver_na_ultima_auditoria_hold>
AUDIT_LOG_PATH:  PROJETOS/QMD/AUDIT-LOG.md
OBSERVACOES:     usar o ultimo relatorio `hold` realmente ativo
```

## Regra Local Adicional

QMD ainda nao possui rodada formal de auditoria. Este wrapper permanece apenas como preset futuro.
