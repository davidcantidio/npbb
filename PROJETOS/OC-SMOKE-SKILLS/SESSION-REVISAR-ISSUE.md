---
doc_id: "SESSION-REVISAR-ISSUE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-SMOKE-SKILLS"
---

# SESSION-REVISAR-ISSUE - Revisao Pos-Issue em Sessao de Chat

## Objetivo

Revisar a issue canario depois do handoff de execucao, mantendo o foco em aderencia do framework.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md`

## Parametros Preenchidos

```text
PROJETO:        OC-SMOKE-SKILLS
FASE:           F1-FUNDACAO
ISSUE_ID:       ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO
ISSUE_PATH:     PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO
BASE_COMMIT:    <resolver_no_handoff_da_issue_canario>
TARGET_COMMIT:  <resolver_no_handoff_da_issue_canario>
EVIDENCIA:      <resolver_no_handoff_da_issue_canario>
OBSERVACOES:    usar o handoff persistido pela execucao do canario; validar aderencia ao guia de smoke e nao apenas mudancas locais
```

## Regra Local Adicional

Este wrapper so entra em jogo quando a issue canario estiver `ready_for_review`.
