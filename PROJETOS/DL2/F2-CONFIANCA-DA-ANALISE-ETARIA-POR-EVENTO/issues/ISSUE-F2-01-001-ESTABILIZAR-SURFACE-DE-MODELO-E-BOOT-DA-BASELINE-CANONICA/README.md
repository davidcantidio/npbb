---
doc_id: "ISSUE-F2-01-001-ESTABILIZAR-SURFACE-DE-MODELO-E-BOOT-DA-BASELINE-CANONICA"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-001 - Estabilizar surface de modelo e boot da baseline canonica

## User Story

Como mantenedor do modulo de leads e dashboards, quero estabilizar a surface canonica de `LeadEvento` e o boot da aplicacao para que a Feature 1 do `DL2` comece sem drift de import ou ambiguidade sobre o agregado de modelos.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: baseline canonica minima para que os readers e writers da analise etaria partam de uma surface estavel.

## Contexto Tecnico

- esta issue reagrupa o trabalho estrutural remanescente de `ISSUE-F1-01-001` com a evidencia parcial ja concluida em `ISSUE-F1-01-003` do legado arquivado
- o objetivo no `DL2` nao e reabrir a issue herdada `done`, e sim fechar a baseline executavel do novo epic com rastreabilidade explicita
- artefato minimo esperado: a aplicacao sobe sem `ImportError` ligado a `LeadEvento`/`LeadEventoSourceKind` e o agregado canonico de modelos fica coerente para a Feature 1

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-01-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-01-001`, When a issue for concluida, Then a aplicacao sobe sem `ImportError` ligado a `LeadEvento`/`LeadEventoSourceKind` e o agregado canonico de modelos fica consistente para os consumidores prioritarios.
- Given a origem complementar herdada, When outro agente ler a issue, Then fica explicito que `ISSUE-F1-01-003` entrou apenas como evidencia parcial e nao como conclusao integral desta issue do `DL2`.
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo.

## Definition of Done da Issue

- [x] a aplicacao sobe sem `ImportError` ligado a `LeadEvento`/`LeadEventoSourceKind`
- [x] o agregado canonico de modelos exposto em `app.models.models` fica consistente com a baseline esperada da Feature 1
- [x] dependencias e links canonicos da issue ficam coerentes com `F2` e `EPIC-F2-01`

## Tasks

- [T1: Estabilizar surface de modelo e boot da baseline canonica](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/models/models.py`
- `backend/app/models/lead_public_models.py`
- `backend/app/services/landing_page_submission.py`
- `backend/app/services/lead_event_service.py`
- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_leads_endpoint.py`
- `backend/tests/test_dashboard_leads_report_endpoint.py`

## Artifact Minimo

A aplicacao sobe sem `ImportError` e a surface canonica de modelos para `LeadEvento` fica estavel para a Feature 1.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F2_DL2_EPICS.md)
- [Epic](../../EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md)
