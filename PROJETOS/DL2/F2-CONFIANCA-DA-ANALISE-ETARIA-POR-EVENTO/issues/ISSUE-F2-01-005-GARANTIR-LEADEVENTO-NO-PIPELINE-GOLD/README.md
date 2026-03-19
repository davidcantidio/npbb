---
doc_id: "ISSUE-F2-01-005-GARANTIR-LEADEVENTO-NO-PIPELINE-GOLD.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-005 - Garantir LeadEvento no pipeline Gold

## User Story

Como mantenedor do modulo de leads e dashboards, quero garantir leadevento no pipeline gold para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-01`.


## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: pipeline Gold garantindo LeadEvento.

## Contexto Tecnico

- o pipeline ja carrega `LeadBatch.evento_id`
- o writer precisa ser idempotente por natureza
- issue pertence a `EPIC-F2-01` na fase `F2` do projeto `DL2`
- artefato minimo esperado: Leads promovidos a Gold asseguram `LeadEvento` quando o lote conhece `evento_id`.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-01-005` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_gold_pipeline.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-01-005`, When a issue for concluida, Then leads promovidos a Gold asseguram `LeadEvento` quando o lote conhece `evento_id`.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [x] Leads promovidos a Gold asseguram `LeadEvento` quando o lote conhece `evento_id`.
- [x] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [x] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Garantir LeadEvento no pipeline Gold](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/lead_pipeline_service.py`
- `backend/app/models/lead_batch.py`
- `backend/tests/test_lead_gold_pipeline.py`

## Artifact Minimo

Leads promovidos a Gold asseguram `LeadEvento` quando o lote conhece `evento_id`.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F2_DL2_EPICS.md)
- [Epic](../../EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md)
- [Issue Dependente](../ISSUE-F2-01-001-ESTABILIZAR-SURFACE-DE-MODELO-E-BOOT-DA-BASELINE-CANONICA/README.md)
- [Issue Dependente](../ISSUE-F2-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO/README.md)
