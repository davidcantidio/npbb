---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F5-03-001-Formalizar-coexistencia-e-onboarding-de-projetos-legados-piloto"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# TASK-1 - Formalizar coexistencia com legados e onboarding do piloto

## objetivo

aprovar o protocolo de entrada de projetos legados e do piloto no FRAMEWORK3

## precondicoes

- definicao de precedencia e bootstrap em F1 concluida

## arquivos_a_ler_ou_tocar

- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `backend/app/models/framework_models.py`

## passos_atomicos

1. definir criterio de entrada de um projeto legado no modulo
2. registrar a metadata minima para onboarding do piloto
3. definir como o filesystem legado convive com o banco e qual piloto e elegivel

## comandos_permitidos

- `rg -n "source_of_truth|project_root_path|audit_log_path" PROJETOS backend/app/models/framework_models.py`

## resultado_esperado

Protocolo de coexistencia e onboarding aprovado.

## testes_ou_validacoes_obrigatorias

- revisao contra o PRD e a governanca do framework

## stop_conditions

- parar se a convivencia exigir migracao em massa de projetos ativos
