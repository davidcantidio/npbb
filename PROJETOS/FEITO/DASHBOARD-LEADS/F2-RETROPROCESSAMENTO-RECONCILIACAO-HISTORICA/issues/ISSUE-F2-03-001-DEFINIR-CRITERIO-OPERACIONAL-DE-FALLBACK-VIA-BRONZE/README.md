---
doc_id: "ISSUE-F2-03-001-DEFINIR-CRITERIO-OPERACIONAL-DE-FALLBACK-VIA-BRONZE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-03-001 - Definir criterio operacional de fallback via bronze

## User Story

Como mantenedor do modulo de leads e dashboards, quero definir criterio operacional de fallback via bronze para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-03`.

## Contexto Tecnico

- o PRD quer criterio operacional explicito
- o reprocessamento ja tem superficie propria no backend
- issue pertence a `EPIC-F2-03` na fase `F2` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: Existe criterio operacional claro para decidir entre backfill direto e fallback via bronze/reprocessamento.

## Plano TDD

- Red: identificar a lacuna documental ou operacional exata no estado atual.
- Green: ajustar apenas o artefato minimo necessario para fechar a lacuna descrita na issue.
- Refactor: revisar consistencia final do documento ou protocolo sem ampliar escopo.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-03-001`, When a issue for concluida, Then existe criterio operacional claro para decidir entre backfill direto e fallback via bronze/reprocessamento.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] Existe criterio operacional claro para decidir entre backfill direto e fallback via bronze/reprocessamento.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Definir criterio operacional de fallback via bronze](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/models/lead_batch.py`
- `PROJETOS/DASHBOARD-LEADS/PRD-DASHBOARD-LEADS.md`

## Artifact Minimo

Existe criterio operacional claro para decidir entre backfill direto e fallback via bronze/reprocessamento.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F2_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F2-03-PROTOCOLO-DE-FALLBACK-VIA-BRONZE.md)
- [Issue Dependente](../ISSUE-F2-02-001-GERAR-RELATORIO-DE-RECONCILIACAO-MISSING-E-AMBIGUOUS/README.md)
