---
doc_id: "INTAKE-RENAME-MODULO-LEAD-IMPORTS.md"
version: "1.0"
status: "approved"
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

# INTAKE - Rename do modulo leads_publicidade para lead_imports

> Intake derivado para planejar o rename futuro de
> `app.modules.leads_publicidade` para `app.modules.lead_imports`, sem executar
> o rename fisico nesta rodada.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `plano_organizacao_import.md`
- item de origem: `rename-module`
- motivo da abertura deste intake: o plano operacional mantinha como pendente
  a escolha de um nome de dominio neutro e uma estrategia de compatibilidade
  para o pacote backend de importacao de leads

## 1. Resumo Executivo

- nome curto da iniciativa: rename modulo lead imports
- tese em 1 frase: fechar a decisao tecnica para migrar futuramente o pacote
  `leads_publicidade` para `lead_imports` com alias temporario de
  compatibilidade
- valor esperado:
  - reduzir acoplamento semantico ao termo `publicidade`
  - deixar claro que o modulo representa a capacidade de importacao de leads
  - evitar um rename transversal sem mapa de consumidores e sem compatibilidade

## 2. Problema ou Oportunidade

- problema atual: `backend/app/modules/leads_publicidade` e o pacote real de
  importacao/ETL de leads, mas o nome mistura um recorte historico de origem
  com uma capacidade que hoje e mais ampla
- evidencia do problema:
  `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
  mostra consumidores em codigo de producao, scripts, testes, imports internos
  do pacote, docs e governanca historica
- custo de nao agir: a nomenclatura antiga continua propagando ambiguidade em
  novos imports e aumenta o custo de uma migracao futura
- por que planejar antes de executar: ha imports diretos e patches por string,
  entao um rename fisico sem alias pode quebrar routers, worker e testes

## 3. Escopo Inicial

### Dentro

- criar governanca propria para o rename
- escolher `app.modules.lead_imports` como nome alvo
- registrar mapa de consumidores por categoria
- definir a estrategia futura de compatibilidade
- atualizar `plano_organizacao_import.md` marcando o rename como planejado,
  nao executado

### Fora

- executar o rename fisico do pacote
- alterar imports de producao, testes ou scripts
- alterar contratos HTTP, schemas, rotas ou comportamento de ETL
- alterar `lead_pipeline/`, `core/leads_etl/`, frontend ou dashboard
- remover referencias historicas em docs/governanca antigas

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- imports atuais por `app.modules.leads_publicidade` continuam funcionando
- rotas sob `/leads` permanecem sem mudanca
- scripts existentes, incluindo `backend/scripts/run_leads_worker.py`,
  permanecem sem mudanca funcional
- schemas, payloads, persistencia e regras de ETL permanecem congelados nesta
  rodada

## 5. Arquitetura Afetada

- backend: pacote futuro `backend/app/modules/lead_imports`
- compatibilidade: pacote antigo `backend/app/modules/leads_publicidade` deve
  permanecer como alias/reexport temporario em uma rodada posterior
- governanca: nova `FEATURE-5` para registrar decisao, impacto e plano de
  migracao

## 6. Riscos Relevantes

- risco tecnico: subestimar imports absolutos internos do proprio pacote
- risco de teste: quebrar mocks e patches por string que usam o caminho antigo
- risco operacional: quebrar worker ou routers por import alterado sem alias
- risco de escopo: confundir planejamento do rename com refatoracao funcional
  de importacao/ETL

## 7. Resultado Esperado e Metricas de Sucesso

- objetivo principal: deixar o rename tecnicamente especificado, com nome alvo
  e compatibilidade definidos
- metricas leading: governanca criada, mapa de consumidores registrado e plano
  operacional atualizado
- criterio minimo para sucesso: nenhum arquivo Python de producao, teste ou
  script alterado nesta rodada

## 8. Follow-ups Deliberadamente Adiados

- criar fisicamente `backend/app/modules/lead_imports`
- migrar imports internos para `app.modules.lead_imports`
- manter `leads_publicidade` como alias temporario
- remover o alias antigo apos busca sem consumidores
- reabrir importacao/ETL funcional em escopo proprio
