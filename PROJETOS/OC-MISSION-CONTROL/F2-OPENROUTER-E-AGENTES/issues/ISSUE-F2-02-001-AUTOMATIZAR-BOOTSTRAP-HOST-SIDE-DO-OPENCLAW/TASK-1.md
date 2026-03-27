---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
tdd_aplicavel: false
---

# T1 - Automatizar bootstrap local e sync remoto

## objetivo

Usar o toolkit host-side para gerar a topologia OpenClaw/OpenRouter localmente e manter o sync remoto compatível com o dashboard atual.

## precondicoes

- toolkit host-side instalado
- OpenClaw CLI disponível
- fluxo remoto do dashboard já funcional

## arquivos_a_ler_ou_tocar

- `src/nemoclaw-host/helper.js`
- `src/nemoclaw-host/common.sh`
- `bin/install-host.sh`
- `config/host.env.example`

## passos_atomicos

1. definir defaults locais para modelos, Telegram e porta do gateway local
2. criar comando idempotente de bootstrap local do OpenClaw
3. ampliar o merge remoto da topologia no helper
4. acoplar o bootstrap local ao `install-host.sh`
5. validar que o dashboard remoto continua operacional

## comandos_permitidos

- `./bin/install-host.sh`
- `~/.local/bin/nemoclaw-hostctl status`
- `~/.local/bin/nemoclaw-hostctl dashboard --no-open`
- `git status --short`

## resultado_esperado

Toolkit host-side reproduz a topologia local e preserva o fluxo remoto existente.

## testes_ou_validacoes_obrigatorias

- checar que o helper cria `~/.openclaw/openclaw.json` quando ausente
- checar que o dashboard remoto continua acessível em `127.0.0.1:18789`
- checar que os placeholders de `host.env` não carregam secrets versionados

## stop_conditions

- parar se a nova automação quebrar o dashboard remoto
- parar se a configuração exigir token real para gerar o scaffold
