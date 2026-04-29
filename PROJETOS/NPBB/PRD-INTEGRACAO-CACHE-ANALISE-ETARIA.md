---
doc_id: "PRD-INTEGRACAO-CACHE-ANALISE-ETARIA.md"
version: "1.0"
status: "active"
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

# PRD - Integracao do cache da analise etaria

> Origem:
> [INTAKE-INTEGRACAO-CACHE-ANALISE-ETARIA.md](INTAKE-INTEGRACAO-CACHE-ANALISE-ETARIA.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-INTEGRACAO-CACHE-ANALISE-ETARIA.md](INTAKE-INTEGRACAO-CACHE-ANALISE-ETARIA.md)
- artefato de origem:
  [PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA.md](../../PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA.md)
- data de criacao: `2026-04-27`
- baseline funcional preservada: endpoint e rota publica de analise etaria ja
  estao habilitados
- baseline estrutural preservada: cache backend por processo, cache frontend
  por chave de query e invalidacao persistida em `dashboard_cache_versions`

## 1. Resumo Executivo

- nome do mini-projeto: integracao cache analise etaria
- tese em 1 frase: concluir a validacao operacional da entrega de cache da
  analise etaria, corrigindo regressao direta quando necessario e fechando a
  decisao de staging com evidencias versionadas
- valor esperado:
  - migration, API, UI e pipeline Gold comprovados em conjunto
  - classificacao clara entre problema novo e legado conhecido
  - consolidacao da evidencia em `artifacts/phase-f4/evidence/`

## 2. Objetivo do PRD

Executar uma rodada full-stack de integracao e remediacao do cache da analise
etaria sem alterar contratos publicos, sem abrir cache distribuido e sem puxar
para esta frente a Fase D de performance estrutural.

## 3. Requisitos Funcionais e Estruturais

1. When a migration for aplicada no ambiente alvo, the system shall criar ou
   manter `dashboard_cache_versions` sem conflito com migrations anteriores.
2. When `GET /dashboard/leads/analise-etaria` for chamado apos startup valido,
   the system shall continuar respondendo com o contrato atual.
3. When user scope, normalized filters, response version and
   `America/Sao_Paulo` reference day permanecerem iguais, the frontend shall
   reutilizar o cache da query sem disparar request repetido fora do fluxo de
   refetch manual.
4. When user scope mudar entre admin, usuario ou agencia, the frontend shall
   not reaproveitar dados em cache de outro escopo.
5. When a Gold batch terminar em `PASS` ou `PASS_WITH_WARNINGS`, the system
   shall incrementar `leads_age_analysis` em `dashboard_cache_versions` com
   `reason` e `source_batch_id`.
6. When a version bump ocorrer, the backend shall parar de reutilizar a entrada
   antiga de cache TTL para a mesma combinacao de filtros e devolver payload
   novo no proximo request.
7. The system shall consolidar profiling, deltas de `pg_stat_statements`,
   `EXPLAIN` e resultados da rodada em `artifacts/phase-f4/evidence/`.
8. The system shall attempt `make ci-quality` before staging sign-off and
   separar falhas em `regression`, `legacy-known` ou `environment`.
9. The system shall not criar nova rota HTTP, novo schema publico, novo
   comportamento de cache distribuido ou redesign funcional do dashboard nesta
   rodada.

## 4. Requisitos Nao Funcionais

- compatibilidade: endpoint, rota de tela e tabela persistida permanecem com o
  mesmo papel publico
- observabilidade: cada bloco de validacao precisa deixar evidencia versionada
  ou motivo explicito de bloqueio
- timezone: qualquer expectativa de referencia diaria usa
  `America/Sao_Paulo`, nao `date.today()` puro
- rollback: rollback de app deve continuar simples porque a tabela nova e
  aditiva e o cache backend e in-memory por processo
- testabilidade: backend, frontend, smoke local e gate do repo precisam ser ao
  menos tentados, mesmo quando houver legado conhecido

## 5. Escopo

### Dentro

- governanca canonica da frente
- pre-voo do workspace
- migration, startup e verificacao estrutural
- validacao backend, frontend e smoke local
- comprovacao de invalidacao por pipeline Gold
- profiling e consolidacao de evidencias
- checklist de staging e notas de rollback

### Fora

- cache distribuido
- refactor estrutural de SQL/MV
- novos contratos publicos
- redesign funcional do dashboard
- remediacoes legadas fora da trilha do cache etario

## 6. Criterios de Aceite

- Given a migration nova,
  when `alembic upgrade head` for executado no ambiente real de dev/staging,
  then `dashboard_cache_versions` existe e nao entra em conflito com o resto do
  schema.
- Given o endpoint de analise etaria,
  when o mesmo usuario repetir filtros e dia de referencia dentro do
  `staleTime`,
  then a UI reutiliza cache sem request redundante.
- Given um usuario admin e um usuario agencia,
  when ambos acessam a tela em sequencia,
  then um escopo nao reaproveita placeholder ou dado do outro.
- Given um lote Gold promovido com sucesso,
  when a tabela `dashboard_cache_versions` for consultada,
  then a versao de `leads_age_analysis` incrementa e o lote aparece em
  `source_batch_id`.
- Given a rodada de validacao,
  when o resumo final for emitido,
  then ele separa bloqueios novos de falhas legadas descritas em `AGENTS.md`.

## 7. Validacao Minima Obrigatoria

- `git status --short`
- `git diff --stat`
- `cd backend && alembic upgrade head`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_dashboard_age_analysis_service.py tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_cache_version_service.py tests/test_lead_gold_pipeline.py`
- `cd frontend && npm run lint && npm run typecheck && npm run test -- --run && npm run build`
- `cd backend && LEADS_AUDIT_EVIDENCE_DIR=../artifacts/phase-f4/evidence python scripts/profile_dashboard_age_analysis.py --label phase-f4`
- `make ci-quality`

> Se `python` nao estiver no PATH do shell, usar explicitamente o interpretador
> do venv conforme `AGENTS.md` e `docs/SETUP.md`.

## 8. Decomposicao Aprovada

- `FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA`
  - `US-10-01`: validar integracao local e remediar regressoes
  - `US-10-02`: consolidar evidencias e liberar staging

## 9. Checklist de Prontidao

- [x] contratos publicos congelados
- [x] evidencia canonica apontada para `artifacts/phase-f4/evidence/`
- [x] criterio de classificacao de falha separado entre legado e regressao nova
- [x] Fase D explicitamente fora do escopo
- [x] estrategia de rollback descrita sem exigir rollback de schema destrutivo
