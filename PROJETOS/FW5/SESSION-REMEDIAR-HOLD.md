---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
project: "FW5"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups caso a auditoria da fase alvo retorne `hold`.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         FW5
FASE:            F1-FUNDACAO
RELATORIO_PATH:  PROJETOS/FW5/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md
AUDIT_LOG_PATH:  PROJETOS/FW5/AUDIT-LOG.md
OBSERVACOES:     nenhuma
```

## Regra Local Adicional

Use este wrapper imediatamente apos uma auditoria com veredito hold.
