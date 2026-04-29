---
doc_id: "INTAKE-INTEGRACAO-CACHE-ANALISE-ETARIA.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-27"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA"
origin_audit_id: "cache-age-analysis-integration"
origin_report_path: "PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA.md"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "backend"
  - "frontend"
  - "alembic"
  - "pipeline-worker"
  - "tests"
  - "docs-governance"
change_type: "integracao-operacional"
audit_rigor: "elevated"
---

# INTAKE - Integracao do cache da analise etaria

> Intake derivado do plano local de integracao do cache da analise etaria para
> transformar uma entrega ja implementada em uma frente canonica de validacao,
> remediacao e prontidao para staging.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- artefato de origem:
  `PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA.md`
- baseline tecnica ja existente no codigo:
  - cache compartilhado no frontend com TanStack Query
  - cache TTL in-memory no backend para `GET /dashboard/leads/analise-etaria`
  - versionamento persistido em `dashboard_cache_versions`
  - bump de versao ao final bem-sucedido do pipeline Gold
- motivo da abertura deste intake: fechar a lacuna entre implementacao parcial
  em codigo e validacao operacional ponta a ponta com evidencias versionadas

## 1. Resumo Executivo

- nome curto da iniciativa: integracao cache analise etaria
- tese em 1 frase: validar e endurecer a entrega ja implementada do cache da
  analise etaria, sem abrir novo contrato publico nem expandir o escopo para
  cache distribuido ou Fase D
- valor esperado:
  - comprovar que a migration, o endpoint, a UI e a invalidacao por Gold operam
    juntos
  - separar regressao nova de problema legado ja conhecido do repo
  - consolidar a trilha de evidencias em `artifacts/phase-f4/evidence/`

## 2. Problema ou Oportunidade

- problema atual: a entrega tecnica existe, mas ainda nao ha fechamento
  canonico de migration, suite ampla, smoke full-stack, profiling e decisao de
  staging
- evidencia do problema:
  - o plano local lista explicitamente os blocos 1-14 de integracao pendentes
  - o codigo ja contem `dashboard_cache_versions`, `useAgeAnalysis`,
    `get_age_analysis_cached` e bump no Gold, mas sem rodada canonica de
    validacao consolidada em `PROJETOS/`
- custo de nao agir: risco de promover para staging uma entrega sem prova
  suficiente de isolamento de cache, invalidacao por pipeline e ausencia de
  regressao
- por que agora: a base tecnica ja esta no tronco e o custo marginal agora e
  fechar observabilidade, confianca operacional e decisao de rollout

## 3. Escopo Inicial

### Dentro

- canonizar a frente em `INTAKE`, `PRD` e `FEATURE-10`
- executar pre-voo, migration, startup e baseline do workspace
- validar backend, frontend e smoke local do dashboard etario
- comprovar invalidacao via pipeline Gold com leitura de
  `dashboard_cache_versions`
- consolidar evidencias em `artifacts/phase-f4/evidence/`
- tentar `make ci-quality` antes de qualquer liberacao para staging

### Fora

- Fase D de fact table, MV ou agregacao SQL estrutural
- redesign funcional do dashboard
- novos endpoints, novos schemas publicos ou nova prop publica de frontend
- cache distribuido
- reabertura ampla de backlog legado fora da trilha do cache etario

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- endpoint `GET /dashboard/leads/analise-etaria`
- rota frontend `/dashboard/leads/analise-etaria`
- tabela de invalidacao `dashboard_cache_versions`
- comportamento de cache por processo no backend atual
- modelo de autorizacao atual por escopo de usuario/agencia

## 5. Riscos Relevantes

- vazamento de cache entre escopos de usuario/agencia no frontend
- invalidacao incompleta apos pipeline Gold bem-sucedido
- conflito de migration ou drift de ambiente entre `.env`, `DATABASE_URL` e
  `DIRECT_URL`
- falso bloqueio por falha legada ja conhecida do repo sendo confundida com
  regressao nova
- expansao indevida do escopo para performance estrutural, redesign de produto
  ou cache distribuido

## 6. Resultado Esperado e Metricas de Sucesso

- migration aplicada sem conflito e tabela `dashboard_cache_versions` validada
- frontend reaproveita cache apenas quando escopo, filtros, dia de referencia e
  versao permanecem iguais
- bump de `leads_age_analysis` observado apos promocao Gold em `PASS` ou
  `PASS_WITH_WARNINGS`
- evidencias novas concentradas em `artifacts/phase-f4/evidence/`
- `make ci-quality` tentado com classificacao final por falha:
  `regression`, `legacy-known` ou `environment`

## 7. Follow-ups Deliberadamente Adiados

- migrar o cache para backend distribuido
- reabrir Fase D de SQL/MV
- redesenhar UX da analise etaria
- transformar os scripts diagnosticos em suite automatica de CI obrigatoria
