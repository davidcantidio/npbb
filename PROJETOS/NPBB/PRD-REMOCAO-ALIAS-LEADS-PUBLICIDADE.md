---
doc_id: "PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS"
origin_audit_id: "remove-legacy-alias"
origin_report_path: "plano_organizacao_import.md"
product_type: "platform-capability"
delivery_surface: "backend-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "backend"
  - "tests"
  - "docs-governance"
change_type: "limpeza-estrutural"
audit_rigor: "elevated"
---

# PRD - Remocao do alias leads_publicidade

> Origem:
> [INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md](INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md](INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md)
- decisao anterior:
  [PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md](PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md)
- data de criacao: `2026-04-23`
- caminho real aprovado: `app.modules.lead_imports`
- caminho legado removido: `app.modules.leads_publicidade`

## 1. Resumo Executivo

- nome do mini-projeto: remocao alias leads publicidade
- tese em 1 frase: encerrar a compatibilidade temporaria do pacote legado
  depois de busca sem consumidores ativos
- valor esperado:
  - caminho unico para imports backend de importacao de leads
  - reducao de ambiguidade para manutencao futura
  - validacao focada sem mexer em comportamento funcional

## 2. Objetivo do PRD

Remover `backend/app/modules/leads_publicidade` e o teste dedicado de
compatibilidade, mantendo `backend/app/modules/lead_imports` como unico caminho
backend real de importacao/ETL de leads.

## 3. Requisitos Funcionais e Estruturais

1. When a limpeza for iniciada, the system shall confirmar ausencia de
   consumidores ativos de `app.modules.leads_publicidade`.
2. When a busca estiver limpa, the system shall remover
   `backend/app/modules/leads_publicidade/**`.
3. When o alias legado for removido, the system shall remover
   `backend/tests/test_lead_imports_compat.py`.
4. Where codigo ativo importar modulos de importacao de leads, the system shall
   usar `app.modules.lead_imports`.
5. The system shall not change HTTP contracts, schemas, routes, ETL behavior,
   frontend, dashboard, `lead_pipeline/` or `core/leads_etl/`.
6. The system shall preserve historical docs/governance references as
   historical evidence.

## 4. Requisitos Nao Funcionais

- compatibilidade: o caminho antigo deixa de ser suportado como interface
  interna Python
- rollback: a rodada e reversivel restaurando os shims removidos se aparecer
  consumidor externo nao mapeado
- testabilidade: buscas e testes focados devem provar que o caminho novo segue
  operante
- seguranca/LGPD: nenhuma nova superficie de dados e criada

## 5. Escopo

### Dentro

- remocao do pacote legado `backend/app/modules/leads_publicidade/**`
- remocao de `backend/tests/test_lead_imports_compat.py`
- governanca `FEATURE-7`
- atualizacao do plano operacional

### Fora

- alteracao funcional de importacao/ETL
- mudanca de rotas, schemas ou payloads
- frontend, dashboard, `lead_pipeline/` e `core/leads_etl/`
- limpeza de referencias historicas antigas em docs/governanca

## 6. Mapa de Impacto

### Producao

- nenhuma alteracao funcional esperada
- imports ativos devem continuar por `app.modules.lead_imports`

### Testes

- remover teste que validava a compatibilidade temporaria
- executar suite focada de ETL/importacao pelo caminho real

### Compatibilidade

- `app.modules.leads_publicidade` deixa de existir como caminho importavel
- `app.modules.lead_imports` permanece o caminho real e suportado

## 7. Criterios de Aceite

- Given consumidores ativos,
  when a busca excluindo shims e o teste dedicado for executada,
  then nao ha ocorrencias de `app.modules.leads_publicidade`.
- Given o pacote backend,
  when a rodada terminar,
  then `backend/app/modules/leads_publicidade` nao existe.
- Given os testes backend,
  when a rodada terminar,
  then `backend/tests/test_lead_imports_compat.py` nao existe.
- Given consumidores ativos,
  when os imports forem revisados,
  then routers, worker, servicos e testes focados continuam preferindo
  `app.modules.lead_imports`.
- Given a rodada estrutural,
  when os testes focados forem executados,
  then comportamento de ETL/importacao permanece preservado.

## 8. Validacao Minima Obrigatoria

- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend/app backend/scripts backend/tests -g "!backend/app/modules/leads_publicidade/**" -g "!backend/tests/test_lead_imports_compat.py"`
- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
- `rg -n "app\\.modules\\.lead_imports|lead_imports" backend/app backend/scripts backend/tests`
- `Test-Path backend/app/modules/leads_publicidade`
- `cd backend && PYTHONPATH=C:\Users\NPBB\npbb;C:\Users\NPBB\npbb\backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py backend/tests/test_etl_rejection_reasons.py backend/tests/test_etl_import_validators.py backend/tests/test_etl_csv_delimiter.py backend/tests/test_leads_import_etl_warning_policy.py backend/tests/test_leads_import_etl_staging_repository.py backend/tests/test_leads_import_etl_endpoint.py backend/tests/test_lead_silver_mapping.py backend/tests/test_lead_ticketing_dedupe_postgres.py`

## 9. Decomposicao Aprovada

- `FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE`
  - `US-7-01`: remover alias leads publicidade

## 10. Checklist de Prontidao

- [x] `app.modules.lead_imports` ja e o pacote real
- [x] consumidores ativos ja foram migrados na `FEATURE-6`
- [x] busca inicial sem consumidores ativos fora dos shims/teste
- [x] importacao/ETL funcional preservada como fora de escopo
