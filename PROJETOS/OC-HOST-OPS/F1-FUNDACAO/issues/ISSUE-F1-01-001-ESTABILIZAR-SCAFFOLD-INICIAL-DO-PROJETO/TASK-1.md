---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"
task_id: "T1"
version: "1.2"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
tdd_aplicavel: false
---

# T1 - Validar o scaffold inicial

## objetivo

Conferir se o scaffold base do projeto continua rastreavel e se o backlog real de host-side agora aponta para o PRD atual.

## precondicoes

- intake real presente
- PRD placeholder substituido
- wrappers locais atualizados

## arquivos_a_ler_ou_tocar

- `PROJETOS/OC-HOST-OPS/INTAKE-OC-HOST-OPS.md`
- `PROJETOS/OC-HOST-OPS/PRD-OC-HOST-OPS.md`
- `PROJETOS/OC-HOST-OPS/SESSION-MAPA.md`
- `PROJETOS/OC-HOST-OPS/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/OC-HOST-OPS/F1-FUNDACAO/F1_OC-HOST-OPS_EPICS.md`
- `PROJETOS/OC-HOST-OPS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md`

## passos_atomicos

1. revisar intake real e PRD em conjunto
2. validar que os wrappers deixam planning como ponto atual
3. corrigir manifests do bootstrap para remover drift documental
4. aprovar a base F1 e registrar o proximo passo do projeto

## comandos_permitidos

- `rg -n "install|restore|launchd|dashboard|Telegram" PROJETOS/OC-HOST-OPS/INTAKE-OC-HOST-OPS.md`
- `rg -n "planning|bootstrap|host-side" PROJETOS/OC-HOST-OPS/SESSION-*.md`
- `git status --short`

## resultado_esperado

Bootstrap encerrado e backlog real do host-side liberado para planning.

## testes_ou_validacoes_obrigatorias

- checar coerencia entre intake, PRD e wrappers
- checar que a issue bootstrap deixa de ser a fila principal do projeto

## stop_conditions

- parar se o PRD voltar a descrever scaffold generico
- parar se wrappers locais continuarem congelados no bootstrap
