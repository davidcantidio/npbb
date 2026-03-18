---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F5-02-001-Definir-dataset-de-treinamento-e-telemetria-de-execucao"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# TASK-1 - Definir contrato do dataset treinavel

## objetivo

aprovar quais campos e sinais entram no dataset de treinamento do FRAMEWORK3

## precondicoes

- historico operacional das fases anteriores disponivel

## arquivos_a_ler_ou_tocar

- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`

## passos_atomicos

1. mapear quais campos treinaveis entram no dataset
2. definir quais sinais de feedback humano e telemetria serao preservados
3. registrar quais campos ficam fora por nao estarem cobertos pelo PRD

## comandos_permitidos

- `rg -n "AgentExecution|approval|evidence|metadata_json" PROJETOS/FRAMEWORK3 backend/app`

## resultado_esperado

Contrato do dataset aprovado.

## testes_ou_validacoes_obrigatorias

- revisao contra as metricas e o objetivo de treinamento do PRD

## stop_conditions

- parar se o contrato exigir dados sensiveis nao cobertos pelo PRD
