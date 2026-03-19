---
doc_id: "ISSUE-F2-01-003-GARANTIR-DUAL-WRITE-NO-SUBMIT-PUBLICO.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-003 - Garantir dual-write no submit publico

## User Story

Como mantenedor do modulo de leads e dashboards, quero garantir dual-write no submit publico para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-01`.


## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: dual-write canonico no submit publico.

## Contexto Tecnico

- o PRD exige `LeadEvento` para todo novo write resolvido por evento
- o fluxo publico e o writer mais sensivel do projeto
- issue pertence a `EPIC-F2-01` na fase `F2` do projeto `DL2`
- artefato minimo esperado: O fluxo publico assegura `LeadEvento` tanto no submit direto do evento quanto no submit associado a ativacao.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-01-003` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_landing_public_endpoints.py tests/test_leads_public_create_endpoint.py -k lead_event` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-01-003`, When a issue for concluida, Then o fluxo publico assegura `LeadEvento` tanto no submit direto do evento quanto no submit associado a ativacao.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [x] O fluxo publico assegura `LeadEvento` tanto no submit direto do evento quanto no submit associado a ativacao.
- [x] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [x] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Garantir dual-write no submit publico](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/landing_page_submission.py`
- `backend/app/services/lead_event_service.py`
- `backend/tests/test_landing_public_endpoints.py`
- `backend/tests/test_leads_public_create_endpoint.py`

## Artifact Minimo

O fluxo publico assegura `LeadEvento` tanto no submit direto do evento quanto no submit associado a ativacao.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F2_DL2_EPICS.md)
- [Epic](../../EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md)
- [Issue Dependente](../ISSUE-F2-01-001-ESTABILIZAR-SURFACE-DE-MODELO-E-BOOT-DA-BASELINE-CANONICA/README.md)
- [Issue Dependente](../ISSUE-F2-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO/README.md)
