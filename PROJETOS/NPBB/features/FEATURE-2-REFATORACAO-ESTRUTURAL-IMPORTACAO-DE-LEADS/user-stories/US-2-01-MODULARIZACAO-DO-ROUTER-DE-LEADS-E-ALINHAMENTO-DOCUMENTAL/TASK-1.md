---
doc_id: "TASK-1.md"
user_story_id: "US-2-01-MODULARIZACAO-DO-ROUTER-DE-LEADS-E-ALINHAMENTO-DOCUMENTAL"
task_id: "T1"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/routers/leads.py"
  - "backend/app/routers/leads_routes/*.py"
tdd_aplicavel: false
---

# T1 - Extrair o router de leads para subrouters internos

## objetivo

Transformar `backend/app/routers/leads.py` em agregador fino, preservando ordem
de registro, imports de compatibilidade e contratos publicos sob `/leads`.

## precondicoes

- baseline funcional da trilha de leads auditada na `FEATURE-1`
- testes focados do backend disponiveis
- proibicao explicita de mudar schema, path ou metodo HTTP

## passos_atomicos

1. criar `backend/app/routers/leads_routes/`
2. distribuir os handlers por contexto: intake publico, lead records,
   referencias, import classico, ETL e batches
3. manter reexportacoes necessarias no agregador para compatibilidade de testes
4. validar import da aplicacao e testes focados do backend

## comandos_permitidos

- `python -m py_compile backend/app/routers/leads.py backend/app/routers/leads_routes/*.py`
- `cd backend && python -m pytest -q tests/test_leads_list_endpoint.py tests/test_leads_public_create_endpoint.py tests/test_lead_batch_endpoints.py tests/test_leads_import_etl_endpoint.py tests/test_lead_silver_mapping.py`

## stop_conditions

- parar se a extracao exigir novo contrato publico
- parar se monkeypatches historicos deixarem de encontrar os simbolos em
  `app.routers.leads`
