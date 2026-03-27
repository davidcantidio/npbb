---
doc_id: "SESSION-IMPLEMENTAR-ISSUE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OC-ISSUE-FIRST-FACTORY"
---

# SESSION-IMPLEMENTAR-ISSUE - Execucao de Issue em Sessao de Chat

## Objetivo

Executar a issue atualmente elegivel do projeto, resolvida a partir da fila documental vigente.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`

## Parametros Preenchidos

```text
PROJETO:     OC-ISSUE-FIRST-FACTORY
FASE:        <resolver_na_fila_atual_do_projeto>
ISSUE_ID:    <resolver_na_fila_atual_do_projeto>
ISSUE_PATH:  <resolver_na_fila_atual_do_projeto>
TASK_ID:     <resolver_na_fila_atual_do_projeto>
```

## Regra Local Adicional

- use `boot-prompt.md` nos niveis de descoberta para resolver a unidade elegivel antes de colar os parametros
- nao trate este wrapper como congelado na F1/bootstrap; a fila atual do projeto prevalece
- se o projeto ainda estiver apenas no scaffold inicial, a issue bootstrap continua sendo a primeira candidata natural
