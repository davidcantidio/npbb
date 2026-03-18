---
doc_id: "SPRINT-F1-01.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
---

# SPRINT-F1-01

## Objetivo da Sprint

Remover a regressao ja introduzida no backend e fechar o contrato base do dominio FRAMEWORK3.

## Capacidade
- story_points_planejados: 4
- issues_planejadas: 3
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Estabilizar baseline do embriao FRAMEWORK3 | 1 | done | [ISSUE-F1-01-001-Estabilizar-baseline-do-embriao-FRAMEWORK3](../issues/ISSUE-F1-01-001-Estabilizar-baseline-do-embriao-FRAMEWORK3/) |
| ISSUE-F1-01-002 | Fechar contrato canonico de entidades IDs e estados | 2 | done | [ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados](../issues/ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados/) |
| ISSUE-F1-03-001 | Definir maquina de estados e gates HITL do orquestrador | 1 | todo | [ISSUE-F1-03-001-Definir-maquina-de-estados-e-gates-HITL-do-orquestrador](../issues/ISSUE-F1-03-001-Definir-maquina-de-estados-e-gates-HITL-do-orquestrador/) |

## Riscos e Bloqueios
- a baseline atual do backend ja esta regressiva quando o router framework e carregado
- qualquer divergencia entre o dominio persistido atual e a governanca canonica bloqueia o fechamento da sprint

## Encerramento
- decisao: pendente
- observacoes: a sprint encerra apenas quando os criterios do objetivo acima estiverem atendidos sem violar os gates aprovados do FRAMEWORK3
