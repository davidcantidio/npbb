---
doc_id: "INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT"
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
change_type: "limpeza-estrutural"
audit_rigor: "elevated"
---

# INTAKE - Decisao sobre DashboardLeads legado

> Intake derivado para fechar a pendencia de destino da tela frontend legada
> `DashboardLeads.tsx`, sem alterar backend, rotas publicas, manifesto de
> dashboard ou a trilha de importacao/ETL.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT`
- artefato de decisao: `plano_organizacao_import.md`
- motivo da abertura deste intake: a rodada anterior consolidou
  `features/leads` e deixou `DashboardLeads.tsx` como legado nao roteado que
  precisava de decisao propria

## 1. Resumo Executivo

- nome curto da iniciativa: decisao DashboardLeads legado
- tese em 1 frase: remover a superficie frontend orfa de dashboard legado,
  preservando o endpoint/script de relatorio e sem habilitar nova rota
- valor esperado:
  - eliminar codigo frontend sem rota publica e sem consumidor ativo
  - reduzir ambiguidade entre a rota atual de analise etaria e a antiga tela
    de conversao
  - manter a referencia historica em governanca e documentacao, nao em codigo
    morto

## 2. Problema ou Oportunidade

- problema atual: `frontend/src/pages/DashboardLeads.tsx` permanece no codigo
  mesmo sem rota publica e com servico frontend exclusivo
- evidencia do problema: `rg -n "DashboardLeads|dashboard_leads|/dashboard/leads/conversao" frontend/src docs PROJETOS plano_organizacao_import.md`
  mostra que as referencias de codigo fonte a `DashboardLeads` e
  `dashboard_leads` estao restritas a esses dois arquivos frontend, enquanto
  `/dashboard/leads/conversao` segue apenas como entrada desabilitada do
  manifesto e teste associado
- custo de nao agir: a tela antiga pode voltar a ser interpretada como
  superficie reutilizavel sem decisao de produto e sem ajuste de UX/testes
- por que agora: a consolidacao do slice `features/leads` ja terminou e a
  pendencia restante de maior alavancagem e fechar o destino do legado

## 3. Escopo Inicial

### Dentro

- criar governanca propria para a decisao
- remover `frontend/src/pages/DashboardLeads.tsx`
- remover `frontend/src/services/dashboard_leads.ts`
- registrar no plano local que o endpoint backend
  `GET /dashboard/leads/relatorio` continua vivo como API/script sem tela
  roteada

### Fora

- alterar `frontend/src/app/AppRoutes.tsx`
- alterar `frontend/src/config/dashboardManifest.ts`
- habilitar `/dashboard/leads/conversao`
- alterar backend, schemas, contratos HTTP ou scripts de relatorio
- alterar importacao/ETL, Bronze, mapeamento ou pipeline
- remover wrappers legados de `pages/*` ou `hooks/*`

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- rota atual habilitada: `/dashboard/leads/analise-etaria`
- entrada de backlog: `/dashboard/leads/conversao` permanece desabilitada no
  manifesto
- endpoint backend: `GET /dashboard/leads/relatorio` permanece disponivel
- shell canonico de importacao: `/leads/importar` permanece congelado

## 5. Arquitetura Afetada

- frontend: remocao da tela legada e do servico exclusivo que so a atendia
- governanca: nova `FEATURE-4` para registrar a decisao de produto/arquitetura
- documentacao operacional: `plano_organizacao_import.md` passa a registrar a
  remocao como concluida

## 6. Riscos Relevantes

- risco tecnico: remover arquivo com consumidor indireto nao detectado
- risco de produto: confundir a remocao da tela frontend com remocao do
  endpoint/script de relatorio
- risco de escopo: aproveitar a limpeza para religar `/dashboard/leads/conversao`
  ou mexer em importacao/ETL

## 7. Resultado Esperado e Metricas de Sucesso

- objetivo principal: remover o legado frontend sem regressao funcional nas
  rotas atuais
- metricas leading: busca `rg` sem referencias de codigo fonte aos arquivos
  removidos; typecheck verde; suite focada de dashboard/manifesto verde
- criterio minimo para sucesso: rotas e manifesto inalterados, backend
  preservado e governanca da decisao criada

## 8. Follow-ups Deliberadamente Adiados

- decidir uma nova tela publica para `/dashboard/leads/conversao`
- redesenhar UX de conversao/evento, caso o produto retome essa pauta
- remover wrappers temporarios de `features/leads`
- reabrir importacao/ETL
