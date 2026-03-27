---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
tdd_aplicavel: false
---

# T1 - Sincronizar workspace versionado com backup e automação local

## objetivo

Garantir que `~/.openclaw/workspace` reflita o snapshot versionado do repositório sempre que o toolkit for instalado ou este clone for atualizado.

## precondicoes

- `openclaw-workspace/` presente no clone
- `rsync` disponível no host
- toolkit host-side usando este repositório como fonte operacional

## arquivos_a_ler_ou_tocar

- `bin/sync-openclaw-workspace.sh`
- `bin/install-host.sh`
- `.githooks/_run-refresh-host-sync.sh`
- `config/host.env.example`
- `bin/validate-host.sh`
- `README.md`
- `openclaw-workspace/README.md`

## passos_atomicos

1. criar um sync idempotente do snapshot versionado para `~/.openclaw/workspace`
2. gerar backup timestampado apenas quando houver mudança real
3. acoplar o sync ao `install-host.sh`
4. acoplar o sync aos hooks locais com comportamento `best-effort`
5. validar marcadores de Assis/QMD no workspace `main`
6. documentar rollout manual, automação e toggle operacional

## comandos_permitidos

- `./bin/sync-openclaw-workspace.sh`
- `./bin/install-host.sh`
- `./bin/validate-host.sh`
- `git status --short`

## resultado_esperado

O workspace `main` local carrega a persona Assis e as regras QMD/OpenClaw sem drift manual, preservando backup antes de sync destrutivo.

## testes_ou_validacoes_obrigatorias

- checar criação de backup em mudança efetiva
- checar bypass com `OPENCLAW_LOCAL_WORKSPACE_SYNC_ENABLED=false`
- checar que o hook continua saindo com código zero
- checar que `bin/validate-host.sh` reconhece Assis/QMD no `main`

## stop_conditions

- parar se o sync automático apagar estado fora de `~/.openclaw/workspace`
- parar se o hook passar a bloquear `git pull` por falha no sync local
