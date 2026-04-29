---
doc_id: "TASK-1.md"
user_story_id: "US-10-02-CONSOLIDAR-EVIDENCIAS-E-LIBERAR-STAGING"
task_id: "T1"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/scripts/profile_dashboard_age_analysis.py"
  - "backend/scripts/run_critical_explains.py"
  - "backend/scripts/capture_pg_stat_statements.py"
  - "artifacts/phase-f4/evidence/"
tdd_aplicavel: false
---

# T1 - Executar drill de invalidacao e consolidar profiling

## objetivo

Comprovar manualmente a invalidacao do cache por pipeline Gold e salvar profiling
e explain no caminho canonico de evidencias da feature.

## precondicoes

- `US-10-01` concluida
- API, worker e banco real disponiveis
- usuario/lote aptos para acionar o pipeline Gold

## orquestracao

- `depends_on`: nenhuma task interna
- `parallel_safe`: `false`
- `write_scope`: scripts diagnosticos e `artifacts/phase-f4/evidence/`

## arquivos_a_ler_ou_tocar

- `backend/scripts/profile_dashboard_age_analysis.py`
- `backend/scripts/run_critical_explains.py`
- `backend/scripts/capture_pg_stat_statements.py`
- `artifacts/phase-f4/evidence/README.md`

## passos_atomicos

1. popular o cache do dashboard etario com a UI ou request direto
2. promover um lote Gold que afete o mesmo recorte do dashboard
3. consultar `dashboard_cache_versions` e registrar o bump de versao
4. rerodar o endpoint/UI e confirmar refresh do dado apos o bump
5. executar profiling, `pg_stat_statements` e `EXPLAIN` salvando tudo em
   `artifacts/phase-f4/evidence/`

## comandos_permitidos

- `cd backend && LEADS_AUDIT_EVIDENCE_DIR=../artifacts/phase-f4/evidence python scripts/profile_dashboard_age_analysis.py --label phase-f4`
- `cd backend && LEADS_AUDIT_EVIDENCE_DIR=../artifacts/phase-f4/evidence python scripts/run_critical_explains.py --profile dashboard_age --label phase-f4`
- `cd backend && LEADS_AUDIT_EVIDENCE_DIR=../artifacts/phase-f4/evidence python scripts/capture_pg_stat_statements.py --profile dashboard_age_analysis --label phase-f4`

## resultado_esperado

Evidencia objetiva de bump persistido, miss pos-bump e artefatos diagnosticos
concentrados no caminho canonico da feature.

## testes_ou_validacoes_obrigatorias

- consulta de `dashboard_cache_versions` antes/depois do Gold
- novo GET da analise etaria apos o bump
- profiling salvo em `artifacts/phase-f4/evidence/`
- explain salvo em `artifacts/phase-f4/evidence/`

## stop_conditions

- parar se nao houver lote controlado para Gold no ambiente alvo
- parar se `DIRECT_URL`/`DATABASE_URL` reais nao permitirem profiling contra
  Postgres
- parar se o bump falhar por problema fora do diff e classificar como
  `environment` ou `legacy-known`
