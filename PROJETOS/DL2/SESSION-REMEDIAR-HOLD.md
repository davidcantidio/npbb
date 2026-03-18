---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
project: "DL2"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups caso a auditoria inicial da fase bootstrap retorne hold.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         DL2
FASE:            F1-FUNDACAO
RELATORIO_PATH:  PROJETOS/DL2/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md
AUDIT_LOG_PATH:  PROJETOS/DL2/AUDIT-LOG.md
OBSERVACOES:     nenhuma
```

## Regra Local Adicional

Use este wrapper imediatamente apos uma auditoria com veredito hold.
