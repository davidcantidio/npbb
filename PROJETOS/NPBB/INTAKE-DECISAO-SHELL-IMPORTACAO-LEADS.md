---
doc_id: "INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS"
origin_audit_id: "plano_organizacao_import"
origin_report_path: "plano_organizacao_import.md"
product_type: "platform-capability"
delivery_surface: "frontend-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "frontend"
  - "docs-governance"
change_type: "decisao-estrutural"
audit_rigor: "elevated"
---

# INTAKE - Decisao sobre shell de importacao de leads

> Intake derivado para decidir a fronteira do shell `/leads/importar`, sem
> mover arquivos, sem alterar comportamento de importacao e sem tocar em ETL,
> Bronze, pipeline, backend ou contratos HTTP.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS`
- artefato de decisao: `plano_organizacao_import.md`
- motivo da abertura deste intake: as limpezas estruturais seguras foram
  concluidas e o bloco restante de leads fora de `features/leads` e o shell
  congelado de importacao

## 1. Resumo Executivo

- nome curto da iniciativa: decisao shell importacao leads
- tese em 1 frase: manter o shell de importacao no local atual enquanto a
  fronteira futura de `features/leads/importacao` e inventariada e decidida
- valor esperado:
  - evitar uma migracao acidental que arraste ETL, Bronze, mapeamento e
    pipeline
  - registrar dependencias reais de `/leads/importar`
  - preparar uma feature posterior de migracao parcial, se aprovada

## 2. Problema ou Oportunidade

- problema atual: `frontend/src/pages/leads/ImportacaoPage.tsx` segue como
  shell canonico da rota `/leads/importar`, mas puxa componentes e telas que
  ainda moram em `frontend/src/pages/leads`
- evidencia do problema: a busca por
  `ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage`
  mostra a rota em `AppRoutes.tsx`, o shell, as telas acopladas e testes ainda
  apontando para `frontend/src/pages/leads`
- custo de agir sem decisao: mover arquivos agora pode quebrar imports
  relativos, reabrir testes fora do gate e misturar organizacao frontend com
  ETL funcional
- por que agora: `FEATURE-8` removeu wrappers nao-import, deixando a importacao
  como o proximo bloco estrutural a ser decidido

## 3. Escopo Inicial

### Dentro

- criar governanca propria para a decisao
- inventariar dependencias do shell `/leads/importar`
- registrar que `ImportacaoPage.tsx` permanece em `frontend/src/pages/leads`
  nesta rodada
- registrar que uma migracao parcial para `features/leads/importacao` so pode
  ocorrer em feature posterior
- atualizar `plano_organizacao_import.md`

### Fora

- mover `ImportacaoPage.tsx`
- mover `frontend/src/pages/leads/importacao/**`
- alterar `MapeamentoPage`, `BatchMapeamentoPage` ou `PipelineStatusPage`
- alterar upload, Bronze, ETL, mapeamento, pipeline, validadores, persistencia
  ou merge policy
- alterar backend, `lead_pipeline/`, `core/leads_etl/`, schemas, rotas
  publicas ou contratos HTTP
- habilitar `/dashboard/leads/conversao`
- recriar wrappers removidos em `FEATURE-8` ou `app.modules.leads_publicidade`

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- rota publica: `/leads/importar`
- shell atual: `frontend/src/pages/leads/ImportacaoPage.tsx`
- redirects/telas relacionadas: mapeamento e pipeline permanecem no desenho
  atual
- contratos HTTP de importacao e ETL permanecem sem mudanca
- pacote backend real permanece `app.modules.lead_imports`

## 5. Arquitetura Afetada

- frontend: apenas documentacao da fronteira atual do shell de importacao
- governanca: nova `FEATURE-9` para registrar a decisao de congelamento e
  preparacao
- documentacao operacional: `plano_organizacao_import.md` passa a registrar a
  decisao e o residual

## 6. Riscos Relevantes

- risco tecnico: transformar decisao documental em refactor funcional
- risco de escopo: misturar shell frontend com backend ETL ou pipeline
- risco de teste: reabrir `ImportacaoPage.test.tsx` sem decidir o gate
- risco operacional: tocar em mudancas locais de dashboard fora desta feature

## 7. Resultado Esperado e Metricas de Sucesso

- objetivo principal: governanca criada e decisao registrada sem diff funcional
- metricas leading: busca de fronteira executada; plano atualizado; nenhum
  arquivo frontend/backend funcional alterado pela rodada
- criterio minimo para sucesso: `/leads/importar` preservado no local atual e
  proxima migracao condicionada a feature posterior

## 8. Follow-ups Deliberadamente Adiados

- migracao parcial de componentes puros para `features/leads/importacao`
- migracao completa do shell em fases
- reabertura funcional de importacao/ETL
- smoke manual em browser para `/leads/importar`
