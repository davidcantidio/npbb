---
doc_id: "SESSION-IMPLEMENTAR-ISSUE.md"
version: "2.1"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SESSION-IMPLEMENTAR-ISSUE - Wrapper SUPABASE

## Objetivo

Fornecer parametros de exemplo e a regra local do projeto SUPABASE sem duplicar
o comportamento normativo da sessao canonica.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`

Este wrapper existe apenas para evitar drift local.

## Parametros de Exemplo

```text
PROJETO:     SUPABASE
FASE:        F2-Migracao-de-Dados
ISSUE_ID:    ISSUE-F2-02-004
ISSUE_PATH:  /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/SUPABASE/F2-Migracao-de-Dados/issues/ISSUE-F2-02-004-Bloquear-Prontidao-Quando-DATABASE_URL-Nao-For-o-Supabase-Alvo.md
TASK_ID:     auto
```

`ISSUE_PATH` pode apontar para:

- arquivo legado `ISSUE-*.md`
- pasta `ISSUE-*/` com `README.md` e `TASK-*.md`

`TASK_ID` e opcional:

- `auto` ou ausente: executa a proxima task elegivel
- `T<N>`: restringe a execucao a uma task especifica da issue

## Regra Local Adicional

- use sempre MCP do Supabase quando houver operacao em recursos da plataforma
- em caso de conflito, `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md` prevalece
