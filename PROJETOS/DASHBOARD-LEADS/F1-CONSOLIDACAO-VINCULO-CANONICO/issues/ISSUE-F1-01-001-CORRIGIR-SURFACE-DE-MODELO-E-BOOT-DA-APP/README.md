---
doc_id: "ISSUE-F1-01-001-CORRIGIR-SURFACE-DE-MODELO-E-BOOT-DA-APP.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Corrigir surface de modelo e boot da app

## User Story

Como mantenedor do modulo de leads e dashboards, quero corrigir surface de modelo e boot da app para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F1-01`.

## Contexto Tecnico

- a app quebra antes da coleta por `ImportError` de `LeadEventoSourceKind`
- landing, pipeline e servicos de dashboard dependem desse agregado de modelos
- issue pertence a `EPIC-F1-01` na fase `F1` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: A aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F1-01-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F1-01-001`, When a issue for concluida, Then a aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] A aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Corrigir surface de modelo e boot da app](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/models/models.py`
- `backend/app/models/lead_public_models.py`
- `backend/app/services/landing_page_submission.py`
- `backend/app/services/lead_event_service.py`

## Artifact Minimo

A aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F1_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F1-01-BASELINE-DE-MODELO-IMPORT-E-MIGRATION.md)
