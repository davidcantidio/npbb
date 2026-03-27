---
doc_id: "SESSION-REVISAR-ISSUE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-MISSION-CONTROL"
---

# SESSION-REVISAR-ISSUE - Revisao Pos-Issue em Sessao de Chat

## Objetivo

Usar este wrapper apenas quando uma nova issue de `OC-MISSION-CONTROL` entrar em `ready_for_review`.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md`

## Parametros Preenchidos

```text
PROJETO:        OC-MISSION-CONTROL
FASE:           <resolver_na_issue_em_ready_for_review>
ISSUE_ID:       <resolver_na_issue_em_ready_for_review>
ISSUE_PATH:     <resolver_na_issue_em_ready_for_review>
BASE_COMMIT:    <resolver_no_handoff_da_issue>
TARGET_COMMIT:  <resolver_no_handoff_da_issue>
EVIDENCIA:      <resolver_no_handoff_da_issue>
OBSERVACOES:    a reconciliacao atual deixou a fila sem issue pendente de review; reutilize este wrapper apenas quando surgir um novo handoff
```

## Regra Local Adicional

- a fila atual do projeto esta em auditoria de fase F2; nao existe issue pendente de review apos a reconciliacao do worktree
- quando uma nova issue entrar em `ready_for_review`, prefira o handoff persistido no manifesto da propria issue
