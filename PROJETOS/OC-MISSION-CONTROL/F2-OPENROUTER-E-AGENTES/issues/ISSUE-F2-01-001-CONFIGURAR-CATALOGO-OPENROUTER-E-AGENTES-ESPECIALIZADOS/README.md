---
doc_id: "ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-001 - Configurar catálogo OpenRouter e agentes especializados

## User Story

Como operador de runtime, quero um trio de agentes com modelos e fallbacks explícitos para que o OpenClaw pare de depender de escolha manual implícita de modelo por tarefa.

## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: catálogo OpenRouter, topologia multi-agent e binding inicial do `planner`.

## Contexto Tecnico

O OpenClaw 2026.2.14 já suporta `agents.list[].model`, `agents.defaults.models` e `bindings[]`. O trabalho desta issue é transformar essa capacidade em uma topologia concreta e reproduzível.

## Plano TDD

- Red: inspecionar a configuração atual e evidenciar a ausência do catálogo OpenRouter e dos agentes especializados
- Green: materializar catálogo, aliases, topologia e binding
- Refactor: simplificar defaults e preservar `main` como fallback compatível

## Criterios de Aceitacao

- [x] `agents.defaults.models` contém os modelos OpenRouter alvo
- [x] `main`, `planner`, `builder` e `auditor` existem em `agents.list[]`
- [x] `planner`, `builder` e `auditor` usam modelos/fallbacks definidos via OpenRouter
- [x] existe binding Telegram `default -> planner`
- [x] `planner` pode delegar para `builder` e `auditor`

## Definition of Done da Issue

- [x] catálogo OpenRouter materializado
- [x] topologia multi-agent aplicada
- [x] binding Telegram do `planner` aplicado
- [x] `main` preservado como fallback fora do OpenRouter

## Tasks

- [T1 - Materializar catálogo e topologia multi-agent](./TASK-1.md)

## Arquivos Reais Envolvidos

- `src/nemoclaw-host/helper.js`
- `src/nemoclaw-host/common.sh`
- `~/.openclaw/openclaw.json`

## Artifact Minimo

- `README.md`
- `TASK-1.md`

## Dependencias

- [Epic](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-01-CATALOGO-OPENROUTER-E-TOPOLOGIA-MULTI-AGENT.md)
- [Fase](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/F2_OC-MISSION-CONTROL_EPICS.md)
- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)
