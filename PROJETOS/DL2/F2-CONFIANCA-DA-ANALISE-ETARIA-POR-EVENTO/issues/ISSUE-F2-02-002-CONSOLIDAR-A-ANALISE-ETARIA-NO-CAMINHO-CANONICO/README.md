---
doc_id: "ISSUE-F2-02-002-CONSOLIDAR-A-ANALISE-ETARIA-NO-CAMINHO-CANONICO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-002 - Consolidar a analise etaria no caminho canonico

## User Story

Como mantenedor do modulo de leads e dashboards, quero consolidar a analise etaria no caminho canonico para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-02`.


## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: reader da analise etaria consolidado no caminho canonico.

## Contexto Tecnico

- o runtime ja esta perto do estado alvo, mas ainda ha drift interno a remover
- issue pertence a `EPIC-F2-02` na fase `F2` do projeto `DL2`
- artefato minimo esperado: O endpoint de analise etaria usa apenas a leitura canonica aprovada e deixa de depender de residuos de uniao transitoria.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-02-002` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_service.py tests/test_dashboard_age_analysis_endpoint.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-02-002`, When a issue for concluida, Then o endpoint de analise etaria usa apenas a leitura canonica aprovada e deixa de depender de residuos de uniao transitoria.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] O endpoint de analise etaria usa apenas a leitura canonica aprovada e deixa de depender de residuos de uniao transitoria.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Consolidar a analise etaria no caminho canonico](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/dashboard_service.py`
- `backend/app/routers/dashboard.py`
- `backend/tests/test_dashboard_age_analysis_service.py`

## Artifact Minimo

O endpoint de analise etaria usa apenas a leitura canonica aprovada e deixa de depender de residuos de uniao transitoria.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F2_DL2_EPICS.md)
- [Epic](../../EPIC-F2-02-ANALISE-ETARIA-NO-CAMINHO-CANONICO-E-COBERTURA-EXECUTAVEL.md)
