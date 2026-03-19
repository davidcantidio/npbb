---
doc_id: "ISSUE-F4-01-001-IMPLEMENTAR-RUNNER-IDEMPOTENTE-DE-BACKFILL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-01-001 - Implementar runner idempotente de backfill

## User Story

Como mantenedor do modulo de leads e dashboards, quero implementar runner idempotente de backfill para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F4-01`.


## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: runner controlado de backfill multi-origem.

## Contexto Tecnico

- o PRD define ordem de resolucao historica
- o runtime ja contem a logica base, mas nao o runner governado
- issue pertence a `EPIC-F4-01` na fase `F4` do projeto `DL2`
- artefato minimo esperado: Existe um runner controlado que materializa `LeadEvento` sem duplicar pares ja existentes.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F4-01-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k backfill` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F4-01-001`, When a issue for concluida, Then existe um runner controlado que materializa `LeadEvento` sem duplicar pares ja existentes.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] Existe um runner controlado que materializa `LeadEvento` sem duplicar pares ja existentes.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Implementar runner idempotente de backfill](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/lead_event_service.py`
- `backend/scripts/`
- `backend/tests/test_lead_event_service.py`

## Artifact Minimo

Existe um runner controlado que materializa `LeadEvento` sem duplicar pares ja existentes.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F4_DL2_EPICS.md)
- [Epic](../../EPIC-F4-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md)
