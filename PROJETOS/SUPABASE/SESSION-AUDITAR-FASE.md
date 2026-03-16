---
doc_id: "SESSION-AUDITAR-FASE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SESSION-AUDITAR-FASE - Wrapper SUPABASE

## Objetivo

Fornecer parametros de exemplo e a regra local do projeto SUPABASE sem duplicar
o comportamento normativo da sessao canonica.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`

Este wrapper existe apenas para evitar drift local.

## Parametros de Exemplo

```text
PROJETO:       SUPABASE
FASE:          F2-Migracao-de-Dados
RODADA:        R01
BASE_COMMIT:   worktree
AUDIT_LOG:     /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/SUPABASE/AUDIT-LOG.md
```

## Regra Local Adicional

- use MCP do Supabase quando a auditoria precisar conferir estado de recursos
  reais da plataforma
- em caso de conflito, `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md` prevalece
