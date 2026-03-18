---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: false
---

# T1 - Validar o scaffold inicial

## objetivo

Conferir se o scaffold gerado pelo script esta completo e sem drift de nomes ou caminhos.

## precondicoes

- projeto novo gerado
- intake, PRD, wrappers e bootstrap F1 presentes

## arquivos_a_ler_ou_tocar

- `PROJETOS/DL2/INTAKE-DL2.md`
- `PROJETOS/DL2/PRD-DL2.md`
- `PROJETOS/DL2/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/DL2/F1-FUNDACAO/F1_DL2_EPICS.md`
- `PROJETOS/DL2/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md`
- `PROJETOS/DL2/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md`

## passos_atomicos

1. revisar a arvore do projeto
2. validar os cabecalhos preenchidos
3. confirmar links e caminhos dos wrappers
4. corrigir placeholders residuais se houver
5. confirmar que a fase F1 e o bootstrap inicial existem

## comandos_permitidos

- `find PROJETOS/DL2 -maxdepth 3 -type f | sort`
- `rg -n "SESSION-PLANEJAR-PROJETO|INTAKE-DL2|PRD-DL2" PROJETOS/DL2`
- `git status --short`

## resultado_esperado

Scaffold inicial pronto para planejamento e execucao.

## testes_ou_validacoes_obrigatorias

- checar que nao ha placeholders em `SESSION-PLANEJAR-PROJETO.md`
- checar que o bootstrap F1 existe
- checar que os caminhos sao repo-relative

## stop_conditions

- parar se algum arquivo esperado nao existir
- parar se houver drift entre nome do arquivo e doc_id
