---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
tdd_aplicavel: false
---

# T1 - Materializar catálogo e topologia multi-agent

## objetivo

Configurar os agentes especializados, o catálogo OpenRouter e o binding Telegram do `planner`.

## precondicoes

- OpenClaw 2026.2.14 disponível
- estrutura do projeto já estabilizada em F1

## arquivos_a_ler_ou_tocar

- `src/nemoclaw-host/helper.js`
- `src/nemoclaw-host/common.sh`
- `~/.openclaw/openclaw.json`

## passos_atomicos

1. definir os modelos alvo e aliases do catálogo
2. aplicar `main/planner/builder/auditor` em `agents.list[]`
3. configurar fallbacks de `builder` e `auditor`
4. criar binding Telegram `default -> planner`
5. validar a topologia por CLI e por leitura do config

## comandos_permitidos

- `openclaw agents list --bindings`
- `openclaw models status`
- `openclaw models status --agent planner`
- `git status --short`

## resultado_esperado

Topologia multi-agent parcial OpenRouter materializada e inspecionável.

## testes_ou_validacoes_obrigatorias

- checar presença de `main/planner/builder/auditor`
- checar binding Telegram do `planner`
- checar catálogo OpenRouter no config

## stop_conditions

- parar se a configuração passar a excluir o modelo primário de `main`
- parar se o binding Telegram conflitar com o fluxo host-side existente
