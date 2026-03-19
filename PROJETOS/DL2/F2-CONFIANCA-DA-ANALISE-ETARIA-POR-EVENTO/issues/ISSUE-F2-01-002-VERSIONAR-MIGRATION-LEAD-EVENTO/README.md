---
doc_id: "ISSUE-F2-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-002 - Versionar migration de lead_evento

## User Story

Como mantenedor do modulo de leads e dashboards, quero versionar migration de lead_evento para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-01`.


## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: migration versionada e rastreavel de lead_evento.

## Contexto Tecnico

- o PRD trata a migration como obrigatoria
- nao ha evidencia versionada de `lead_evento` no historico atual de Alembic
- issue pertence a `EPIC-F2-01` na fase `F2` do projeto `DL2`
- artefato minimo esperado: Existe uma migration versionada e rastreavel para `lead_evento`, aderente ao modelo SQLModel atual.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-01-002` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_alembic_single_head.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-01-002`, When a issue for concluida, Then existe uma migration versionada e rastreavel para `lead_evento`, aderente ao modelo SQLModel atual.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] Existe uma migration versionada e rastreavel para `lead_evento`, aderente ao modelo SQLModel atual.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Versionar migration de lead_evento](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/alembic/versions/`
- `backend/app/models/lead_public_models.py`
- `backend/app/models/models.py`

## Artifact Minimo

Existe uma migration versionada e rastreavel para `lead_evento`, aderente ao modelo SQLModel atual.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F2_DL2_EPICS.md)
- [Epic](../../EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md)
- [Issue Dependente](../ISSUE-F2-01-001-ESTABILIZAR-SURFACE-DE-MODELO-E-BOOT-DA-BASELINE-CANONICA/README.md)
