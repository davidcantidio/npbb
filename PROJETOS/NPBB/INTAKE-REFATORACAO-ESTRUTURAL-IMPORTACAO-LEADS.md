---
doc_id: "INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-22"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
origin_audit_id: "RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS"
origin_report_path: "PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS.md"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "backend"
  - "frontend"
  - "docs-governance"
change_type: "refatoracao-estrutural"
audit_rigor: "elevated"
---

# INTAKE - Refatoracao estrutural da importacao de leads

> Intake derivado para abrir um mini-projeto de remediacao estrutural, sem
> alterar contratos publicos de backend ou frontend.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD`
- auditoria de origem:
  `RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS`
- relatorio de origem:
  `PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS.md`
- motivo da abertura deste intake: reduzir o hotspot estrutural da trilha de
  leads sem reabrir a feature funcional ja auditada

## 1. Resumo Executivo

- nome curto da iniciativa: refatoracao estrutural da importacao de leads
- tese em 1 frase: modularizar o roteador de leads, consolidar o shell canonico
  de importacao e alinhar a documentacao sem quebrar contratos
- valor esperado em 3 linhas:
  - diminuir acoplamento no router `backend/app/routers/leads.py`
  - remover duplicacao interna entre dashboard e lista de leads no frontend
  - documentar a superficie canonica real da trilha `/leads` e
    `/dashboard/leads`

## 2. Problema ou Oportunidade

- problema atual: a importacao de leads concentra backend, frontend e docs em
  poucos arquivos com responsabilidade excessiva
- evidencia do problema: `backend/app/routers/leads.py` acumula multiplos
  contextos de rota; `useReferenciaEventos` estava isolado em uma pagina de
  dashboard apesar de ser compartilhado; a documentacao ainda descreve rotas
  antigas ou ambiguas
- custo de nao agir: a manutencao da trilha de leads continua arriscada,
  dificultando rollback simples e evolucoes incrementais
- por que agora: ha um plano aprovado para uma primeira rodada nao quebravel,
  com rollback trivial por revert e sem ampliar escopo funcional

## 3. Escopo Inicial

### Dentro

- extrair subrouters internos para `backend/app/routers/leads_routes/*`
- manter `backend/app/routers/leads.py` como agregador fino
- mover `useReferenciaEventos` para `frontend/src/hooks/useReferenciaEventos.ts`
- simplificar a rota `/leads/importar` com lazy-load direto de
  `pages/leads/ImportacaoPage`
- atualizar docs para refletir o shell canonico `/leads/importar`, redirects
  legados e a rota real `/dashboard/leads/analise-etaria`

### Fora

- migracoes de banco
- rename de pacote ou modulo
- mudanca de contrato HTTP, schema ou rota publica
- intervencoes em `lead_pipeline/`, `core/leads_etl/` ou rename de
  `app.modules.leads_publicidade`
- remediacoes funcionais P0/P1 de ownership ja descritas no diagnostico

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- frontend:
  `/leads`, `/leads/importar`, `/leads/mapeamento`, `/leads/pipeline`
- dashboard: `/dashboard/leads` continua redirecionando para
  `/dashboard/leads/analise-etaria`
- backend: todos os endpoints e schemas FastAPI sob `/leads`, incluindo paths
  com e sem trailing slash
- docs: registrar explicitamente que `/dashboard/leads/relatorio` segue como
  API/script e nao como tela roteada nesta rodada

## 5. Arquitetura Afetada

- backend: `backend/app/routers/leads.py` e novos submodulos internos em
  `backend/app/routers/leads_routes/`
- frontend: `frontend/src/app/AppRoutes.tsx`,
  `frontend/src/pages/leads/LeadsListPage.tsx`,
  `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx` e hook compartilhado
- documentacao: `docs/WORKFLOWS.md`, docs de dashboard e manual operacional
- governanca: intake, PRD e `FEATURE-2` dedicados em `PROJETOS/NPBB`

## 6. Riscos Relevantes

- risco tecnico: a extracao do router pode quebrar imports indiretos usados em
  testes e monkeypatches
- risco documental: docs antigas podem continuar apontando para `/dashboard/leads`
  sem detalhar o redirect real
- risco operacional: remover o wrapper de importacao sem manter query params ou
  redirects legados causaria regressao de navegacao

## 7. Resultado Esperado e Metricas de Sucesso

- objetivo principal: reduzir acoplamento estrutural da trilha de leads sem
  regressao funcional
- metricas leading: testes focados de leads passando; typecheck do frontend
  verde; import da app FastAPI preservado
- criterio minimo para considerar sucesso: a refatoracao ser aplicada por
  revert simples, sem mudar contratos publicos e sem novas regressões na trilha
  de leads

## 8. Follow-ups Deliberadamente Adiados

- `lead_pipeline/` e `core/leads_etl/`
- rename amplo de `app.modules.leads_publicidade`
- move maior para `frontend/src/features/leads`
- decisao de produto sobre expor ou remover `DashboardLeads.tsx`
