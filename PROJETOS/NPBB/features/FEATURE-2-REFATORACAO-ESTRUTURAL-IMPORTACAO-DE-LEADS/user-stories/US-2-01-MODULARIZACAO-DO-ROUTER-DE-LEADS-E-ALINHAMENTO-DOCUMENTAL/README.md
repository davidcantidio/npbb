---
doc_id: "US-2-01-MODULARIZACAO-DO-ROUTER-DE-LEADS-E-ALINHAMENTO-DOCUMENTAL"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
task_instruction_mode: "required"
feature_id: "FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS"
decision_refs: []
---

# US-2-01 - Modularizacao do router de leads e alinhamento documental

## User Story

Como engenharia do NPBB, quero quebrar o router de leads em subrouters internos
e alinhar a documentacao operacional para reduzir acoplamento sem quebrar a
superficie publica da trilha de importacao.

## Feature de Origem

- **Feature**: `FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS`
- **Comportamento coberto**: extracao estrutural do backend e alinhamento de
  docs sem mudanca de contrato HTTP

## Contexto Tecnico

`backend/app/routers/leads.py` concentrava multiplos contextos de rota e os
docs ainda descreviam superfices antigas ou ambiguidade entre a rota de tela e
o endpoint agregado de dashboard. Esta US fecha a fatia backend + docs da
refatoracao incremental.

## Criterios de Aceitacao (Given / When / Then)

- **Given** o router publico `app.routers.leads`,
  **when** a aplicacao sobe,
  **then** todos os endpoints existentes de `/leads` continuam registrados com
  os mesmos contratos.
- **Given** os testes que monkeypatcham simbolos em `app.routers.leads`,
  **when** a modularizacao interna e aplicada,
  **then** as reexportacoes necessarias continuam acessiveis pelo agregador.
- **Given** a documentacao operacional de leads e dashboard,
  **when** um operador consulta os fluxos suportados,
  **then** o shell canonico, os redirects legados e a rota real do dashboard
  ficam explicitos.

## Tasks

- [T1 - Extrair o router de leads para subrouters internos](./TASK-1.md)
- [T2 - Atualizar docs operacionais e registrar divergencias reais de rota](./TASK-2.md)

## Arquivos Reais Envolvidos

- `backend/app/routers/leads.py`
- `backend/app/routers/leads_routes/*.py`
- `backend/tests/test_leads_list_endpoint.py`
- `backend/tests/test_leads_public_create_endpoint.py`
- `backend/tests/test_lead_batch_endpoints.py`
- `backend/tests/test_leads_import_etl_endpoint.py`
- `backend/tests/test_lead_silver_mapping.py`
- `docs/WORKFLOWS.md`
- `docs/MANUAL-NPBB.md`
- `docs/tela-inicial/menu/Dashboard/leads_dashboard.md`

## Dependencias

- [Feature 2](../../FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS.md)
- [PRD estrutural](../../../../PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)
