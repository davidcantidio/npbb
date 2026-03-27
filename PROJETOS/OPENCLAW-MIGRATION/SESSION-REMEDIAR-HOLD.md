---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OPENCLAW-MIGRATION"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria

## Objetivo

Roteiar follow-ups apos auditoria `hold` de uma feature de
`OPENCLAW-MIGRATION`.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

## Parametros Preenchidos

```text
PROJETO:         OPENCLAW-MIGRATION
FEATURE_ID:      <resolver_na_ultima_auditoria_hold>
FEATURE_PATH:    <resolver_na_ultima_auditoria_hold>
RELATORIO_PATH:  <resolver_na_ultima_auditoria_hold>
AUDIT_LOG_PATH:  /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/PROJETOS/OPENCLAW-MIGRATION/AUDIT-LOG.md
OBSERVACOES:     nenhuma
```

## Regra Local Adicional

- use este wrapper apenas quando houver um `hold` real aberto no projeto
- descubra `FEATURE_ID`, `FEATURE_PATH` e `RELATORIO_PATH` a partir do
  `AUDIT-LOG.md` e da pasta `features/`
- nao use `FASE` como parametro de entrada novo

