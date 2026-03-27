---
doc_id: "EPIC-F2-01-CATALOGO-OPENROUTER-E-TOPOLOGIA-MULTI-AGENT.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
---

# EPIC-F2-01 - Catalogo OpenRouter e topologia multi-agent

## Objetivo

Explicitar no runtime OpenClaw quais agentes existem, quais modelos cada um usa e como o ingresso inicial do Telegram é roteado.

## Resultado de Negocio Mensuravel

O operador deixa de escolher modelos manualmente por tentativa e passa a contar com um trio especializado já configurado.

## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: catálogo OpenRouter, agentes `planner/builder/auditor` e binding inicial do `planner`.

## Contexto Arquitetural

- `~/.openclaw/openclaw.json`
- `agents.defaults.models`
- `agents.list[]`
- `bindings[]`
- `channels.telegram.*`

## Definition of Done do Epico

- [x] catálogo OpenRouter presente com aliases
- [x] `main`, `planner`, `builder` e `auditor` materializados
- [x] `planner` possui binding Telegram configurado
- [x] delegação mínima `planner -> builder/auditor` foi prevista

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS | Configurar catálogo OpenRouter e agentes especializados | Tornar explícita a topologia multi-agent e os modelos por agente. | 5 | done | [ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS) | Feature 2 |

## Artifact Minimo do Epico

- `README.md` da issue
- `TASK-1.md`

## Dependencias

- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)
- [Fase](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/F2_OC-MISSION-CONTROL_EPICS.md)
