---
doc_id: "SESSION-AUDITAR-FASE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-SMOKE-SKILLS"
---

# SESSION-AUDITAR-FASE - Auditoria de Fase em Sessao de Chat

## Objetivo

Auditar a fase canario F1-FUNDACAO quando a issue bootstrap tiver passado por execucao e revisao.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`

## Parametros Preenchidos

```text
PROJETO:      OC-SMOKE-SKILLS
FASE:         F1-FUNDACAO
RODADA:       R01
BASE_COMMIT:  worktree
AUDIT_LOG:    PROJETOS/OC-SMOKE-SKILLS/AUDIT-LOG.md
```

## Regra Local Adicional

O relatorio base da fase fica em `PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`, mas a auditoria formal so deve ocorrer depois do canario gerar evidencia real.
