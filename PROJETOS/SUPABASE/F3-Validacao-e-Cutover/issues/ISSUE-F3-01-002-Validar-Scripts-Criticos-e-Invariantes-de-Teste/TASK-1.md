---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-01-002-Validar-Scripts-Criticos-e-Invariantes-de-Teste"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T1 - Revisar scripts criticos contra o contrato atual de conexao

## objetivo

Confirmar que os scripts criticos do backend continuam usando o contrato de conexao correto apos o cutover.

## precondicoes

- ISSUE-F3-01-001 concluida ou sem bloqueios de runtime

## arquivos_a_ler_ou_tocar

- `backend/scripts/seed_common.py`
- `backend/scripts/seed_domains.py`
- `backend/scripts/seed_sample.py`
- `backend/.env.example`

## passos_atomicos

1. revisar em `seed_common.py` a preferencia por `DIRECT_URL` para operacoes sensiveis
2. revisar em `seed_domains.py` e `seed_sample.py` como esses scripts consomem o helper comum ou as variaveis de ambiente
3. confirmar que nenhum deles assume PostgreSQL local como requisito padrao
4. registrar qualquer divergencia objetiva antes da etapa documental

## comandos_permitidos

- `rg -n "DIRECT_URL|DATABASE_URL|sqlite" backend/scripts/seed_common.py backend/scripts/seed_domains.py backend/scripts/seed_sample.py backend/.env.example`

## resultado_esperado

Scripts criticos coerentes com o contrato atual de conexao.

## testes_ou_validacoes_obrigatorias

- confirmar que scripts sensiveis preferem `DIRECT_URL` quando apropriado

## stop_conditions

- parar se algum script critico ainda assumir banco local como fluxo principal
