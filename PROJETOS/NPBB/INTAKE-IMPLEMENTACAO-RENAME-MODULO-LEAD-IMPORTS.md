---
doc_id: "INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md"
version: "1.0"
status: "approved"
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

# INTAKE - Implementacao do rename do modulo lead imports

> Intake derivado da `FEATURE-5-RENAME-MODULO-LEAD-IMPORTS` para executar o
> rename fisico planejado de `app.modules.leads_publicidade` para
> `app.modules.lead_imports`, mantendo compatibilidade temporaria.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `plano_organizacao_import.md`
- decisao de origem: `FEATURE-5-RENAME-MODULO-LEAD-IMPORTS`
- nome alvo aprovado: `app.modules.lead_imports`
- estrategia aprovada: pacote novo como implementacao real e pacote antigo
  como alias/reexport temporario

## 1. Resumo Executivo

- nome curto da iniciativa: implementacao rename modulo lead imports
- tese em 1 frase: mover a implementacao real para `lead_imports` sem quebrar
  consumidores legados do caminho `leads_publicidade`
- valor esperado:
  - reduzir ambiguidade semantica no backend
  - estabelecer o novo caminho preferencial para codigo ativo
  - preservar rollback e compatibilidade durante a migracao incremental

## 2. Problema ou Oportunidade

- problema atual: `backend/app/modules/leads_publicidade` ainda e o pacote real
  de importacao/ETL de leads
- evidencia: routers, worker, servicos e testes ainda importavam
  `app.modules.leads_publicidade`
- oportunidade: executar o rename planejado em uma rodada restrita, com shims
  de compatibilidade e testes focados

## 3. Escopo Inicial

### Dentro

- criar `backend/app/modules/lead_imports` como pacote real
- transformar `backend/app/modules/leads_publicidade` em compatibilidade
  temporaria
- migrar imports ativos de producao, script e testes focados para
  `app.modules.lead_imports`
- adicionar teste explicito para import legado profundo e monkeypatch por
  string
- atualizar governanca e plano operacional

### Fora

- alterar comportamento de ETL, persistencia, validadores ou merge policy
- alterar contratos HTTP, schemas ou rotas publicas
- alterar frontend, dashboard, `lead_pipeline/` ou `core/leads_etl/`
- remover o alias antigo nesta rodada
- reescrever docs/governanca historicas apenas para trocar o nome antigo

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- novo caminho preferencial: `app.modules.lead_imports.*`
- caminho legado temporario: `app.modules.leads_publicidade.*`
- rotas sob `/leads` permanecem sem mudanca de contrato
- scripts atuais devem continuar executando com o mesmo comportamento
- regras de validacao, persistencia, merge e DQ permanecem inalteradas

## 5. Riscos Relevantes

- quebrar imports profundos do caminho legado
- duplicar objetos de modulo e fazer monkeypatch atingir apenas o shim
- alterar comportamento funcional durante a movimentacao do pacote
- confundir esta rodada com reabertura de importacao/ETL funcional

## 6. Resultado Esperado e Metricas de Sucesso

- `backend/app/modules/lead_imports` existe e contem a implementacao real
- imports ativos usam `app.modules.lead_imports`
- `app.modules.leads_publicidade` continua importavel como compatibilidade
- testes focados de ETL/importacao passam
- busca por `app.modules.leads_publicidade` em codigo ativo fica restrita a
  shims e teste/documentacao de compatibilidade

## 7. Follow-ups Deliberadamente Adiados

- remover `backend/app/modules/leads_publicidade`
- limpar referencias historicas antigas
- mover outros slices frontend de leads
- reabrir importacao/ETL funcional
