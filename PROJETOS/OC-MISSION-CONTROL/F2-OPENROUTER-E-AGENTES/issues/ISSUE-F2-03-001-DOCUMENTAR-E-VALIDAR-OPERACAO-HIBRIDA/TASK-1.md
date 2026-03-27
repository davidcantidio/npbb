---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-20"
tdd_aplicavel: false
---

# T1 - Publicar runbook e checks da topologia

## objetivo

Tornar a topologia OpenClaw/OpenRouter legível para a operação diária e verificável por script.

## precondicoes

- topologia multi-agent definida
- bootstrap host-side implementado

## arquivos_a_ler_ou_tocar

- `README.md`
- `bin/validate-host.sh`

## passos_atomicos

1. documentar o trio `main/planner/builder/auditor`
2. explicar o papel do Telegram no ingresso do `planner`
3. listar os comandos de verificação por CLI
4. automatizar checks adicionais no `validate-host.sh`
5. garantir que os checks não exijam tokens reais para passar

## comandos_permitidos

- `./bin/validate-host.sh`
- `openclaw agents list --bindings`
- `openclaw models status`
- `git status --short`

## resultado_esperado

Runbook curto e validação local cobrindo a topologia OpenClaw/OpenRouter.

## testes_ou_validacoes_obrigatorias

- checar presença dos quatro agentes
- checar binding Telegram do `planner`
- checar catálogo OpenRouter no config

## stop_conditions

- parar se o validate-host passar a depender de token real
- parar se a documentação divergir da configuração produzida pelo bootstrap
