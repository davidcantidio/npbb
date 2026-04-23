---
doc_id: "PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-5-RENAME-MODULO-LEAD-IMPORTS"
origin_audit_id: "rename-module"
origin_report_path: "plano_organizacao_import.md"
product_type: "platform-capability"
delivery_surface: "backend-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "backend"
  - "scripts"
  - "tests"
  - "docs-governance"
change_type: "implementacao-estrutural"
audit_rigor: "elevated"
---

# PRD - Implementacao do rename do modulo lead imports

> Origem:
> [INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md](INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md](INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md)
- decisao anterior:
  [PRD-RENAME-MODULO-LEAD-IMPORTS.md](PRD-RENAME-MODULO-LEAD-IMPORTS.md)
- data de criacao: `2026-04-23`
- nome alvo aprovado: `app.modules.lead_imports`

## 1. Resumo Executivo

- nome do mini-projeto: implementacao rename modulo lead imports
- tese em 1 frase: executar o rename planejado do pacote backend de importacao
  de leads com compatibilidade temporaria para consumidores legados
- valor esperado:
  - novo caminho de dominio neutro para codigo ativo
  - manutencao de compatibilidade para imports profundos antigos
  - reducao de risco por validacao focada antes de remover o alias

## 2. Objetivo do PRD

Implementar `backend/app/modules/lead_imports` como pacote real de
importacao/ETL de leads, mantendo `backend/app/modules/leads_publicidade` como
camada temporaria de compatibilidade, sem alterar comportamento funcional.

## 3. Requisitos Funcionais e Estruturais

1. When a implementacao for migrada, the system shall expor
   `app.modules.lead_imports` como caminho preferencial.
2. When um consumidor legado importar `app.modules.leads_publicidade`, the
   system shall manter o import funcionando temporariamente.
3. When um import legado profundo apontar para um modulo folha, the system
   shall resolver para o mesmo objeto de modulo usado por `lead_imports`.
4. When testes usarem monkeypatch por string no caminho legado, the system
   shall aplicar o patch no modulo real.
5. The system shall migrate active production, script and focused test imports
   to `app.modules.lead_imports`.
6. The system shall not change HTTP contracts, schemas, routes, ETL behavior,
   frontend, dashboard, `lead_pipeline/` or `core/leads_etl/`.

## 4. Requisitos Nao Funcionais

- compatibilidade: caminho antigo permanece vivo ate feature posterior
- rollback: a rodada e reversivel restaurando imports para o caminho antigo e
  removendo o pacote novo
- testabilidade: testes focados devem provar novo caminho e compatibilidade
  legada
- seguranca/LGPD: nenhuma nova superficie de dados e criada

## 5. Escopo

### Dentro

- pacote real `backend/app/modules/lead_imports`
- shims em `backend/app/modules/leads_publicidade`
- imports ativos em routers, worker, servicos e testes focados
- governanca `FEATURE-6`
- atualizacao do plano operacional

### Fora

- alteracao funcional de importacao/ETL
- mudanca de rotas, schemas ou payloads
- frontend, dashboard, `lead_pipeline/` e `core/leads_etl/`
- remocao do alias antigo
- reescrita de docs historicas antigas

## 6. Mapa de Impacto

### Producao

- routers de importacao em `backend/app/routers/leads_routes/`
- `backend/app/services/lead_pipeline_service.py`

### Scripts

- `backend/scripts/run_leads_worker.py`

### Testes

- testes backend de ETL, persistencia, warning policy, merge policy, silver
  mapping, ticketing dedupe e endpoints
- teste dedicado de compatibilidade legado/novo

### Compatibilidade

- `backend/app/modules/leads_publicidade/**` passa a ser camada temporaria de
  alias para `backend/app/modules/lead_imports/**`

## 7. Criterios de Aceite

- Given o pacote backend,
  when a rodada terminar,
  then `backend/app/modules/lead_imports` contem a implementacao real.
- Given consumidores ativos,
  when os imports forem revisados,
  then routers, worker, servicos e testes focados preferem
  `app.modules.lead_imports`.
- Given consumidores legados,
  when imports profundos em `app.modules.leads_publicidade` forem executados,
  then eles continuam funcionando.
- Given monkeypatch por string no caminho legado,
  when o patch for aplicado,
  then o modulo real em `lead_imports` recebe a alteracao.
- Given a rodada estrutural,
  when os testes focados forem executados,
  then comportamento de ETL/importacao permanece preservado.

## 8. Validacao Minima Obrigatoria

- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade|app\\.modules\\.lead_imports|lead_imports" backend docs PROJETOS plano_organizacao_import.md`
- `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`
- `Get-ChildItem -Recurse -Depth 3 backend/app/modules/lead_imports`
- `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_lead_imports_compat.py backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py backend/tests/test_etl_rejection_reasons.py backend/tests/test_etl_import_validators.py backend/tests/test_etl_csv_delimiter.py backend/tests/test_leads_import_etl_warning_policy.py backend/tests/test_leads_import_etl_staging_repository.py backend/tests/test_leads_import_etl_endpoint.py backend/tests/test_lead_silver_mapping.py backend/tests/test_lead_ticketing_dedupe_postgres.py`

## 9. Decomposicao Aprovada

- `FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS`
  - `US-6-01`: implementar rename do modulo lead imports

## 10. Checklist de Prontidao

- [x] nome alvo escolhido em `FEATURE-5`
- [x] compatibilidade temporaria definida
- [x] importacao/ETL funcional preservada como fora de escopo
- [x] remocao do alias antigo adiada para feature posterior
