---
doc_id: "SPRINT-F4-01.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# SPRINT-F4-01

## Objetivo da Sprint

Selecionar unidade executavel preparar work order e rodar o loop base de execucao.

## Capacidade
- story_points_planejados: 7
- issues_planejadas: 5
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F4-01-001 | Selecionar proxima task elegivel e montar work order executavel | 2 | todo | [ISSUE-F4-01-001-Selecionar-proxima-task-elegivel-e-montar-work-order-executavel](../issues/ISSUE-F4-01-001-Selecionar-proxima-task-elegivel-e-montar-work-order-executavel/) |
| ISSUE-F4-01-002 | Preparar sessao operacional e preflight de bloqueios | 1 | todo | [ISSUE-F4-01-002-Preparar-sessao-operacional-e-preflight-de-bloqueios](../issues/ISSUE-F4-01-002-Preparar-sessao-operacional-e-preflight-de-bloqueios/) |
| ISSUE-F4-02-001 | Orquestrar execucao sequencial de tasks da issue | 2 | todo | [ISSUE-F4-02-001-Orquestrar-execucao-sequencial-de-tasks-da-issue](../issues/ISSUE-F4-02-001-Orquestrar-execucao-sequencial-de-tasks-da-issue/) |
| ISSUE-F4-02-002 | Registrar commit evidencia e fechamento por task | 1 | todo | [ISSUE-F4-02-002-Registrar-commit-evidencia-e-fechamento-por-task](../issues/ISSUE-F4-02-002-Registrar-commit-evidencia-e-fechamento-por-task/) |
| ISSUE-F4-02-003 | Tratar retry stop conditions e coordenacao de subagentes | 1 | todo | [ISSUE-F4-02-003-Tratar-retry-stop-conditions-e-coordenacao-de-subagentes](../issues/ISSUE-F4-02-003-Tratar-retry-stop-conditions-e-coordenacao-de-subagentes/) |

## Riscos e Bloqueios
- qualquer ambiguidade de ordenacao entre tasks compromete o resolvedor da proxima unidade executavel
- stop conditions e retries mal definidos podem corromper o estado operacional

## Encerramento
- decisao: pendente
- observacoes: a sprint encerra apenas quando os criterios do objetivo acima estiverem atendidos sem violar os gates aprovados do FRAMEWORK3
