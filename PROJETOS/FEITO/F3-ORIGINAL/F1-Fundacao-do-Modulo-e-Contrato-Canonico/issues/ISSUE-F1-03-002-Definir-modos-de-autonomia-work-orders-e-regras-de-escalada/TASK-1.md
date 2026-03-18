---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-03-002-Definir-modos-de-autonomia-work-orders-e-regras-de-escalada"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# TASK-1 - Definir modos de autonomia e regras de escalada

## objetivo

fechar a taxonomia operacional de autonomia e o payload minimo de work order

## precondicoes

- `ISSUE-F1-03-001` concluida

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/GOV-WORK-ORDER.md`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`

## passos_atomicos

1. fechar taxonomia final de modos de autonomia por projeto
2. mapear em quais passos do algoritmo o PM sempre aprova
3. definir criterios de retry escalada BLOQUEADO e campos minimos de work order

## comandos_permitidos

- `rg -n "AgentMode|ExecutionPrepare|ReviewIssue|TaskComplete|work_order" PROJETOS backend/app`

## resultado_esperado

Contrato operacional de autonomia e work order aprovado.

## testes_ou_validacoes_obrigatorias

- revisao contra `GOV-WORK-ORDER.md` e `PROJETOS/Algoritmo.md`

## stop_conditions

- parar se o PM exigir modo adicional fora da taxonomia aprovada
