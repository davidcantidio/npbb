---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados"
task_id: "T1"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: false
---

# TASK-1 - Fechar contrato canonicode entidades estados e taxonomias

## objetivo

definir a matriz canonica de entidades estados e IDs do FRAMEWORK3

## precondicoes

- `ISSUE-F1-01-001` concluida

## arquivos_a_ler_ou_tocar

- `PROJETOS/FRAMEWORK3/INTAKE-FRAMEWORK3.md`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`

## passos_atomicos

1. mapear divergencias entre intake PRD governanca e o modelo atual
2. normalizar taxonomias como `intake_kind` e demais enums controlados
3. definir matriz canonica de `project intake prd phase epic sprint issue task agent_execution` e seus estados

## comandos_permitidos

- `rg -n "intake_kind|status|approval|audit_gate|canonical_id" PROJETOS/FRAMEWORK3 backend/app/models/framework_models.py backend/app/schemas/framework.py`

## resultado_esperado

Contrato documental aprovado para o dominio FRAMEWORK3.

## testes_ou_validacoes_obrigatorias

- revisao do contrato contra `GOV-INTAKE.md`, `GOV-SCRUM.md` e `GOV-ISSUE-FIRST.md`

## stop_conditions

- parar se houver conflito nao resolvivel entre governanca canonica e PRD
