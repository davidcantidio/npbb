---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-20"
project: "OC-MISSION-CONTROL"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups caso a auditoria inicial da fase bootstrap retorne hold.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         OC-MISSION-CONTROL
FASE:            F1-FUNDACAO
RELATORIO_PATH:  PROJETOS/OC-MISSION-CONTROL/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md
AUDIT_LOG_PATH:  PROJETOS/OC-MISSION-CONTROL/AUDIT-LOG.md
OBSERVACOES:     nenhuma
```

## Regra Local Adicional

Use este wrapper imediatamente apos uma auditoria com veredito hold.
