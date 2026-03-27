---
doc_id: "SESSION-IMPLEMENTAR-TASK.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
---

# SESSION-IMPLEMENTAR-TASK - Execucao com entrada na Task

## Objetivo

Executar uma **task** concreta (`TASK-*.md`) com leitura ascendente ate PRD/Intake
e delegacao ao fluxo operacional de user story.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-TASK.md`

## Parametros Preenchidos

```text
PROJETO:    ATIVOS-INGRESSOS
TASK_PATH:  <caminho completo para PROJETOS/ATIVOS-INGRESSOS/features/.../TASK-N.md>
ROUND:      1
```

## Regra Local Adicional

- prefira esta sessao quando a task alvo ja for conhecida (commit atomico, TDD por
  task); use `SESSION-IMPLEMENTAR-US.md` com `TASK_ID: auto` quando a fila ainda
  tiver de ser resolvida na US
- nao congele caminhos da bootstrap; a fila real do projeto prevalece
