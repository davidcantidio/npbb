---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-20"
project: "OC-SMOKE-SKILLS"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups caso a auditoria inicial da fase bootstrap retorne hold.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         OPENCLAW-MIGRATION
FASE:            NÃO SE APLICA
RELATORIO_PATH:  /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md
AUDIT_LOG_PATH:  /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/PROJETOS/OPENCLAW-MIGRATION/AUDIT-LOG.md
OBSERVACOES:     nenhuma
```

## Regra Local Adicional

Use este wrapper imediatamente apos uma auditoria com veredito hold.
