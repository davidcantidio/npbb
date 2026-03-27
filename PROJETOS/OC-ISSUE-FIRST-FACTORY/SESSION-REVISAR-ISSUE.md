---
doc_id: "SESSION-REVISAR-ISSUE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OC-ISSUE-FIRST-FACTORY"
---

# SESSION-REVISAR-ISSUE - Revisao Pos-Issue em Sessao de Chat

## Objetivo

Revisar a issue atualmente em `ready_for_review` ou a issue explicitamente indicada pelo PM.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md`

## Parametros Preenchidos

```text
PROJETO:        OC-ISSUE-FIRST-FACTORY
FASE:           <resolver_no_handoff_ou_na_issue_alvo>
ISSUE_ID:       <resolver_no_handoff_ou_na_issue_alvo>
ISSUE_PATH:     <resolver_no_handoff_ou_na_issue_alvo>
BASE_COMMIT:    <resolver_no_handoff_ou_na_issue_alvo>
TARGET_COMMIT:  <resolver_no_handoff_ou_na_issue_alvo>
EVIDENCIA:      <resolver_no_handoff_ou_na_issue_alvo>
OBSERVACOES:    usar o handoff persistido na issue alvo sempre que existir
```

## Regra Local Adicional

- resolva primeiro a issue `ready_for_review` vigente do projeto; so use override manual quando o PM trouxer evidencia reproduzivel
- este wrapper nao fixa a revisao na bootstrap; a issue alvo muda conforme a fila
- em caso de conflito, o handoff persistido na issue continua sendo a fonte de verdade
