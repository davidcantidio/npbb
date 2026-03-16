---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SESSION-REMEDIAR-HOLD - Wrapper SUPABASE

## Objetivo

Fornecer parametros de exemplo e a regra local do projeto SUPABASE sem duplicar
o comportamento normativo da sessao canonica.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`

Este wrapper existe apenas para evitar drift local.

## Parametros de Exemplo

```text
PROJETO:        SUPABASE
FASE:           F2-Migracao-de-Dados
RELATORIO_PATH: /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/SUPABASE/F2-Migracao-de-Dados/auditorias/RELATORIO-AUDITORIA-F2-R01.md
AUDIT_LOG_PATH: /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/SUPABASE/AUDIT-LOG.md
OBSERVACOES:    nenhuma
```

## Regra Local Adicional

- use MCP do Supabase quando a remediacao envolver recursos gerenciados da
  plataforma
- em caso de conflito, `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md` prevalece
