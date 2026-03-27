---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OC-ISSUE-FIRST-FACTORY"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups caso a auditoria inicial da fase bootstrap retorne hold.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         OC-ISSUE-FIRST-FACTORY
FASE:            <resolver_na_ultima_auditoria_hold>
RELATORIO_PATH:  <resolver_na_ultima_auditoria_hold>
AUDIT_LOG_PATH:  PROJETOS/OC-ISSUE-FIRST-FACTORY/AUDIT-LOG.md
OBSERVACOES:     usar o ultimo relatorio `hold` realmente ativo
```

## Regra Local Adicional

- use este wrapper apenas quando houver um `hold` real aberto no projeto
- resolva fase e relatorio a partir do `AUDIT-LOG.md`, nao do scaffold inicial
