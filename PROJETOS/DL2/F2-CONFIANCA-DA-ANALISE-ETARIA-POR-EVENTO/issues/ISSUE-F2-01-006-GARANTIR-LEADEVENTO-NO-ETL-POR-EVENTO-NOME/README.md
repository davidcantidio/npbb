---
doc_id: "ISSUE-F2-01-006-GARANTIR-LEADEVENTO-NO-ETL-POR-EVENTO-NOME.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-006 - Garantir LeadEvento no ETL por evento_nome

## User Story

Como mantenedor do modulo de leads e dashboards, quero garantir leadevento no etl por evento_nome para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-01`.


## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: ETL por evento_nome resolvendo LeadEvento de forma deterministica.

## Contexto Tecnico

- o PRD aceita `evento_nome` apenas como backfill deterministico
- essa issue prepara o comportamento correto para F2
- issue pertence a `EPIC-F2-01` na fase `F2` do projeto `DL2`
- artefato minimo esperado: O ETL cria `LeadEvento` apenas quando a resolucao por nome e unica e deterministica.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-01-006` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_silver_mapping.py -k evento` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-01-006`, When a issue for concluida, Then o ETL cria `LeadEvento` apenas quando a resolucao por nome e unica e deterministica.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] O ETL cria `LeadEvento` apenas quando a resolucao por nome e unica e deterministica.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Garantir LeadEvento no ETL por evento_nome](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/modules/leads_publicidade/application/etl_import/persistence.py`
- `backend/app/services/lead_event_service.py`
- `backend/tests/test_lead_silver_mapping.py`

## Artifact Minimo

O ETL cria `LeadEvento` apenas quando a resolucao por nome e unica e deterministica.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F2_DL2_EPICS.md)
- [Epic](../../EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md)
- [Issue Dependente](../ISSUE-F2-01-001-ESTABILIZAR-SURFACE-DE-MODELO-E-BOOT-DA-BASELINE-CANONICA/README.md)
- [Issue Dependente](../ISSUE-F2-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO/README.md)
