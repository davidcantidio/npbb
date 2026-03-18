---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-02-001-Formalizar-sincronizacao-precedencia-e-bootstrap-Markdown-banco"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# TASK-1 - Definir precedencia e bootstrap minimo do projeto

## objetivo

aprovar quem prevalece entre Markdown e banco e como nasce um projeto FRAMEWORK3

## precondicoes

- `ISSUE-F1-01-002` concluida

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/GOV-WORK-ORDER.md`
- `PROJETOS/FRAMEWORK3/INTAKE-FRAMEWORK3.md`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `backend/app/models/framework_models.py`

## passos_atomicos

1. decidir fonte primaria e fallback em caso de divergencia
2. definir como nasce `AUDIT-LOG.md` e os paths minimos de um projeto
3. registrar como normalizar intake e PRD existentes e como armazenar estado de sincronizacao

## comandos_permitidos

- `rg -n "source_of_truth|audit_log_path|file_path|document_path" PROJETOS backend/app/models/framework_models.py`

## resultado_esperado

Protocolo de bootstrap e precedencia aprovado.

## testes_ou_validacoes_obrigatorias

- revisao do protocolo contra `GOV-ISSUE-FIRST.md` e `GOV-WORK-ORDER.md`

## stop_conditions

- parar se a precedencia exigir mudar a regra de fonte de verdade dos projetos legados
