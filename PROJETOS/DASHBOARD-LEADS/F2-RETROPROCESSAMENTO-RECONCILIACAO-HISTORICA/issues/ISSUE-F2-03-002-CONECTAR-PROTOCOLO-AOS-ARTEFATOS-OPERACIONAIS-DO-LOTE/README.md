---
doc_id: "ISSUE-F2-03-002-CONECTAR-PROTOCOLO-AOS-ARTEFATOS-OPERACIONAIS-DO-LOTE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-03-002 - Conectar protocolo aos artefatos operacionais do lote

## User Story

Como mantenedor do modulo de leads e dashboards, quero conectar protocolo aos artefatos operacionais do lote para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-03`.

## Contexto Tecnico

- a issue fecha o elo entre protocolo e operacao real do lote
- nao abre automacao de reprocessamento fora do que o repositorio ja suporta
- issue pertence a `EPIC-F2-03` na fase `F2` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: O protocolo referencia claramente os artefatos e pontos de entrada existentes para fallback controlado.

## Plano TDD

- Red: identificar a lacuna documental ou operacional exata no estado atual.
- Green: ajustar apenas o artefato minimo necessario para fechar a lacuna descrita na issue.
- Refactor: revisar consistencia final do documento ou protocolo sem ampliar escopo.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-03-002`, When a issue for concluida, Then o protocolo referencia claramente os artefatos e pontos de entrada existentes para fallback controlado.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] O protocolo referencia claramente os artefatos e pontos de entrada existentes para fallback controlado.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Conectar protocolo aos artefatos operacionais do lote](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/app/models/lead_batch.py`

## Artifact Minimo

O protocolo referencia claramente os artefatos e pontos de entrada existentes para fallback controlado.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F2_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F2-03-PROTOCOLO-DE-FALLBACK-VIA-BRONZE.md)
- [Issue Dependente](../ISSUE-F2-03-001-DEFINIR-CRITERIO-OPERACIONAL-DE-FALLBACK-VIA-BRONZE/README.md)
