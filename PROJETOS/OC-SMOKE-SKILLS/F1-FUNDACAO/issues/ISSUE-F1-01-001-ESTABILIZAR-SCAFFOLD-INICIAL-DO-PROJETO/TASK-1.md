---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"
task_id: "T1"
version: "1.2"
status: "todo"
owner: "PM"
last_updated: "2026-03-23"
tdd_aplicavel: false
---

# T1 - Validar o canario do framework

## objetivo

Conferir se o projeto-canario esta alinhado ao `GUIA-TESTE-SKILLS.md` e ao framework atual.

## precondicoes

- intake, PRD, wrappers e bootstrap F1 presentes
- `GUIA-TESTE-SKILLS.md` atualizado

## arquivos_a_ler_ou_tocar

- `PROJETOS/OC-SMOKE-SKILLS/INTAKE-OC-SMOKE-SKILLS.md`
- `PROJETOS/OC-SMOKE-SKILLS/PRD-OC-SMOKE-SKILLS.md`
- `PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-MAPA.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/F1_OC-SMOKE-SKILLS_EPICS.md`
- `PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md`
- `PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md`

## passos_atomicos

1. revisar intake, PRD e guia do canario em conjunto
2. validar que os wrappers locais apontam para o canario atual
3. confirmar que a issue bootstrap continua sendo a prova controlada de execucao
4. rodar ou preparar a validacao via `./bin/check-openclaw-smoke.sh`
5. registrar qualquer drift encontrado como correcao do framework compartilhado

## comandos_permitidos

- `find PROJETOS/OC-SMOKE-SKILLS -maxdepth 3 -type f | sort`
- `rg -n "GUIA-TESTE-SKILLS|SESSION-|check-openclaw-smoke" PROJETOS/OC-SMOKE-SKILLS`
- `./bin/check-openclaw-smoke.sh`
- `git status --short`

## resultado_esperado

Canario pronto para provar o framework atual com baixo blast radius.

## testes_ou_validacoes_obrigatorias

- checar que intake, PRD e guia concordam sobre o escopo do canario
- checar que o bootstrap F1 existe
- checar que os caminhos sao repo-relative

## stop_conditions

- parar se algum arquivo esperado nao existir
- parar se houver drift entre guia, wrappers e backlog bootstrap
