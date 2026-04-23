---
doc_id: "INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-22"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS"
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
change_type: "refatoracao-estrutural"
audit_rigor: "elevated"
---

# INTAKE - Organizacao frontend de leads nao-import

> Intake derivado para organizar apenas a superficie nao-import de leads no
> frontend, mantendo rotas publicas, contratos de servico e o freeze de
> importacao/ETL.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS`
- artefato de decisao: `plano_organizacao_import.md`
- motivo da abertura deste intake: concluir a proxima rodada estrutural segura
  do frontend de leads sem reabrir a trilha de importacao

## 1. Resumo Executivo

- nome curto da iniciativa: organizacao frontend de leads nao-import
- tese em 1 frase: mover lista, analise etaria e hook compartilhado para um
  slice `features/leads` com compatibilidade temporaria nos caminhos legados
- valor esperado em 3 linhas:
  - reduzir acoplamento interno entre `pages/*` e logica de leads
  - manter `/leads` e `/dashboard/leads/analise-etaria` inalterados
  - registrar `DashboardLeads.tsx` como artefato legado nao roteado

## 2. Problema ou Oportunidade

- problema atual: a superficie nao-import de leads ainda esta espalhada entre
  `pages/leads`, `pages/dashboard` e `hooks`, apesar de representar a mesma
  vertical funcional
- evidencia do problema: `LeadsListPage`, `LeadsAgeAnalysisPage`,
  `useAgeAnalysisFilters` e `useReferenciaEventos` permanecem em diretorios
  diferentes, enquanto outras areas do frontend ja usam `features/*`
- custo de nao agir: a evolucao dessa area continua exigindo navegacao por
  multiplos caminhos e aumenta o risco de novos acoplamentos ao shell de
  importacao
- por que agora: a rodada estrutural anterior fechou backend, docs e shell
  canonico de importacao; a proxima fatia segura ficou explicitamente reservada
  para o frontend nao-import

## 3. Escopo Inicial

### Dentro

- criar `frontend/src/features/leads/` com subpastas `list/`, `dashboard/` e
  `shared/`
- mover para esse slice a implementacao atual de `LeadsListPage`,
  `LeadsAgeAnalysisPage`, `useAgeAnalysisFilters`, `useReferenciaEventos`,
  `leadsListExport` e `leadsListQuarterPresets`
- manter wrappers finos nos caminhos legados em `pages/*` e `hooks/*`
- documentar `DashboardLeads.tsx` como legado nao roteado e fora desta rodada

### Fora

- qualquer mudanca em `ImportacaoPage.tsx` e `pages/leads/importacao/**`
- qualquer mudanca em `PipelineStatusPage.tsx`, `MapeamentoPage.tsx` ou
  `BatchMapeamentoPage.tsx`
- qualquer mudanca em backend, `lead_pipeline/` ou `core/leads_etl/`
- religar rota ou manifesto para `/dashboard/leads/conversao`

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- rotas React: `/leads`, `/leads/importar`, `/dashboard/leads` e
  `/dashboard/leads/analise-etaria`
- manifesto de dashboard: `/dashboard/leads/analise-etaria` segue habilitada e
  `/dashboard/leads/conversao` segue desabilitada
- imports legados de `pages/*` e `hooks/useReferenciaEventos` continuam
  validos via reexport temporario
- nenhum tipo ou shape de `services/leads_import`,
  `services/dashboard_age_analysis` ou `services/dashboard_leads` muda

## 5. Arquitetura Afetada

- frontend: novo slice `frontend/src/features/leads/`
- compatibilidade: wrappers legados em `frontend/src/pages/*` e
  `frontend/src/hooks/useReferenciaEventos.ts`
- governanca: `PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md` e `FEATURE-3`

## 6. Riscos Relevantes

- risco tecnico: quebrar imports relativos ao mover os arquivos para o novo
  slice
- risco de compatibilidade: wrappers incompletos podem quebrar testes ou
  imports legados
- risco de produto: `DashboardLeads.tsx` voltar a ser interpretado como rota
  ativa sem decisao formal

## 7. Resultado Esperado e Metricas de Sucesso

- objetivo principal: deixar a superficie nao-import de leads agrupada em
  `features/leads` sem regressao funcional
- metricas leading: `npm run typecheck` verde; suites focadas do recorte verdes
- criterio minimo para considerar sucesso: rotas e manifesto inalterados,
  wrappers legados funcionais e `DashboardLeads.tsx` explicitamente fora do
  escopo executado

## 8. Follow-ups Deliberadamente Adiados

- remocao dos reexports temporarios
- decisao de produto sobre transformar `DashboardLeads.tsx` em tela publica
- qualquer retomada do freeze de importacao/ETL
