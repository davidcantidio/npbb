---
doc_id: "TASK-1.md"
us_id: "US-1-01-BOOTSTRAP"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
tdd_aplicavel: false
---

# T1 - Validar o scaffold inicial

## objetivo

Conferir se o scaffold gerado pelo script esta completo e sem drift de
nomes, wrappers ou caminhos.

## precondicoes

- projeto novo gerado
- intake, PRD, wrappers e feature bootstrap presentes

## arquivos_a_ler_ou_tocar

- `PROJETOS/DASHBOARD-ATIVOS/INTAKE-DASHBOARD-ATIVOS.md`
- `PROJETOS/DASHBOARD-ATIVOS/PRD-DASHBOARD-ATIVOS.md`
- `PROJETOS/DASHBOARD-ATIVOS/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/DASHBOARD-ATIVOS/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/DASHBOARD-ATIVOS/SESSION-REVISAR-US.md`
- `PROJETOS/DASHBOARD-ATIVOS/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/DASHBOARD-ATIVOS/features/FEATURE-1-FOUNDATION/FEATURE-1.md`
- `PROJETOS/DASHBOARD-ATIVOS/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/README.md`
- `PROJETOS/DASHBOARD-ATIVOS/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/TASK-1.md`

## passos_atomicos

1. revisar a arvore do projeto
2. validar os cabecalhos preenchidos
3. confirmar links e caminhos dos wrappers
4. confirmar a ausencia de `F1-*`, `issues/` e `sprints/`
5. corrigir placeholders residuais se houver

## comandos_permitidos

- `find PROJETOS/DASHBOARD-ATIVOS -maxdepth 5 -type f | sort`
- `rg -n "SESSION-PLANEJAR-PROJETO|SESSION-IMPLEMENTAR-US|FEATURE-1|US-1-01" PROJETOS/DASHBOARD-ATIVOS`
- `git status --short`

## resultado_esperado

Scaffold inicial pronto para planejamento e execucao no paradigma
`Feature -> User Story -> Task`.

## testes_ou_validacoes_obrigatorias

- checar que nao ha placeholders residuais em `SESSION-PLANEJAR-PROJETO.md`
- checar que a feature bootstrap existe
- checar que os caminhos sao repo-relative

## stop_conditions

- parar se algum arquivo esperado nao existir
- parar se houver drift entre nome do arquivo e doc_id
