---
doc_id: "PRD-RENAME-MODULO-LEAD-IMPORTS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "plano_organizacao_import"
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
change_type: "planejamento-estrutural"
audit_rigor: "elevated"
---

# PRD - Rename do modulo leads_publicidade para lead_imports

> Origem:
> [INTAKE-RENAME-MODULO-LEAD-IMPORTS.md](INTAKE-RENAME-MODULO-LEAD-IMPORTS.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-RENAME-MODULO-LEAD-IMPORTS.md](INTAKE-RENAME-MODULO-LEAD-IMPORTS.md)
- data de criacao: `2026-04-23`
- decisao operacional de suporte: `plano_organizacao_import.md`
- nome alvo aprovado: `app.modules.lead_imports`

## 1. Resumo Executivo

- nome do mini-projeto: rename modulo lead imports
- tese em 1 frase: planejar o rename futuro de `leads_publicidade` para
  `lead_imports` com alias temporario de compatibilidade
- valor esperado:
  - estabelecer nome neutro para a capacidade de importacao de leads
  - reduzir risco de rename amplo com consumidores nao mapeados
  - preservar funcionamento atual ate uma rodada propria de migracao

## 2. Objetivo do PRD

Definir nome alvo, mapa de impacto e estrategia de compatibilidade para um
rename futuro do pacote backend de importacao de leads, sem alterar codigo
funcional nesta rodada.

## 3. Requisitos Funcionais e Estruturais

1. When o rename for planejado, the system shall registrar
   `app.modules.lead_imports` como nome alvo.
2. When o mapa tecnico for registrado, the system shall categorizar
   consumidores em producao, scripts, testes, codigo interno do pacote e
   docs/governanca.
3. When a estrategia futura for definida, the system shall prever
   `backend/app/modules/lead_imports` como pacote real.
4. When a compatibilidade for definida, the system shall manter
   `backend/app/modules/leads_publicidade` como alias/reexport temporario em
   uma rodada futura de implementacao.
5. The system shall not alter imports Python, scripts, rotas, schemas,
   persistencia, ETL funcional, frontend ou dashboard nesta rodada.
6. The system shall preserve referencias historicas em docs e governanca
   antigas, atualizando apenas documentos da rodada atual e o plano
   operacional.

## 4. Requisitos Nao Funcionais

- compatibilidade: caminho antigo deve continuar disponivel ate migracao
  validada
- rollback: a rodada atual e documental e reversivel por remocao dos artefatos
  de governanca e reversao do plano
- testabilidade: comandos de mapeamento devem ser registrados; suites
  funcionais so sao obrigatorias se codigo Python for alterado
- seguranca/LGPD: nenhuma nova superficie de dados sera criada

## 5. Escopo

### Dentro

- governanca da decisao
- mapa de consumidores do caminho antigo
- escolha de nome alvo
- plano de compatibilidade e migracao posterior
- atualizacao do plano local

### Fora

- rename fisico
- alteracao de imports ou patches
- alteracao de backend funcional, scripts, schemas ou rotas
- frontend, dashboard, `lead_pipeline/` e `core/leads_etl/`

## 6. Mapa de Impacto

### Producao

- `backend/app/routers/leads_routes/classic_import.py`
- `backend/app/routers/leads_routes/etl_import.py`
- `backend/app/services/lead_pipeline_service.py`

### Scripts

- `backend/scripts/run_leads_worker.py`

### Testes

- imports diretos em testes de ETL, persistencia, warning policy, merge policy,
  silver mapping, ticketing dedupe e endpoints
- patches por string em
  `backend/tests/test_leads_import_etl_staging_repository.py`

### Codigo interno do pacote

- imports absolutos em
  `backend/app/modules/leads_publicidade/application/etl_import/preview_service.py`
- imports absolutos em
  `backend/app/modules/leads_publicidade/application/etl_import/persistence.py`

### Docs e governanca historica

- referencias em ADRs, intakes, PRDs, features e auditorias anteriores devem
  permanecer como evidencia historica, salvo documentos desta rodada e plano
  operacional

## 7. Criterios de Aceite

- Given a governanca da rodada,
  when os artefatos forem revisados,
  then o nome alvo `app.modules.lead_imports` esta registrado.
- Given o mapa tecnico,
  when a busca por `leads_publicidade` for executada,
  then os consumidores aparecem classificados no PRD ou na user story.
- Given o codigo backend,
  when a rodada terminar,
  then nenhum import de producao, teste ou script foi alterado.
- Given o plano operacional,
  when a rodada terminar,
  then `rename-module` esta marcado como planejado, nao executado.

## 8. Validacao Minima Obrigatoria

- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
- `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`

Se algum codigo Python for alterado por engano, executar tambem:

- `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py`

## 9. Decomposicao Aprovada

- `FEATURE-5-RENAME-MODULO-LEAD-IMPORTS`
  - `US-5-01`: mapear e planejar rename do modulo lead imports

## 10. Checklist de Prontidao

- [x] nome alvo escolhido: `lead_imports`
- [x] rename fisico explicitamente fora desta rodada
- [x] compatibilidade temporaria definida
- [x] consumidores conhecidos mapeados
- [x] importacao/ETL funcional preservada
