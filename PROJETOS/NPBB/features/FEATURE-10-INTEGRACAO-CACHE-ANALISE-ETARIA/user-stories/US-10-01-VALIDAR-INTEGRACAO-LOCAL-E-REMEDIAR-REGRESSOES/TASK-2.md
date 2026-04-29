---
doc_id: "TASK-2.md"
user_story_id: "US-10-01-VALIDAR-INTEGRACAO-LOCAL-E-REMEDIAR-REGRESSOES"
task_id: "T2"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/services/dashboard_service.py"
  - "backend/app/services/dashboard_cache_version_service.py"
  - "backend/app/core/dashboard_cache.py"
  - "backend/app/models/dashboard_cache.py"
  - "backend/app/services/lead_pipeline_service.py"
  - "backend/alembic/versions/0c1d2e3f4a5b_create_dashboard_cache_versions.py"
  - "backend/tests/test_dashboard_age_analysis_service.py"
  - "backend/tests/test_dashboard_age_analysis_endpoint.py"
  - "backend/tests/test_dashboard_cache_version_service.py"
  - "backend/tests/test_lead_gold_pipeline.py"
tdd_aplicavel: false
---

# T2 - Validar backend e corrigir regressoes diretas do cache

## objetivo

Executar a bateria focada de backend, corrigir regressoes diretas do cache da
analise etaria e classificar o restante como legado conhecido ou falha de
ambiente.

## precondicoes

- `T1` concluida com migration e startup verificados
- banco de teste ou fallback SQLite disponivel conforme `AGENTS.md`
- stack de backend pronta para executar pytest

## orquestracao

- `depends_on`: `T1`
- `parallel_safe`: `false`
- `write_scope`: arquivos backend e testes da trilha do cache etario

## arquivos_a_ler_ou_tocar

- `backend/app/services/dashboard_service.py`
- `backend/app/services/dashboard_cache_version_service.py`
- `backend/app/core/dashboard_cache.py`
- `backend/app/models/dashboard_cache.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/tests/test_dashboard_age_analysis_service.py`
- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_cache_version_service.py`
- `backend/tests/test_lead_gold_pipeline.py`

## passos_atomicos

1. rodar a suite focada de backend para cache, endpoint e Gold
2. analisar cada falha e classificar em `regression`, `legacy-known` ou
   `environment`
3. corrigir somente regressoes diretas desta trilha
4. rerodar a bateria focada apos cada correcao
5. tentar a suite backend ampla e registrar claramente o que for legado

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_dashboard_age_analysis_service.py tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_cache_version_service.py tests/test_lead_gold_pipeline.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q`
- `rg -n "leads_age_analysis|dashboard_cache_versions|get_age_analysis_cached|bump_dashboard_cache_version" backend`

## resultado_esperado

Suite focada de backend verde ou com bloqueios explicitamente classificados,
sem regressao direta do cache etario pendente.

## testes_ou_validacoes_obrigatorias

- suite focada de backend acima
- rerun da suite focada apos qualquer correcao
- tentativa documentada da suite backend ampla

## stop_conditions

- parar se a correcao exigir novo contrato HTTP ou schema publico
- parar se a falha observada reproduzir exatamente o legado conhecido do
  `AGENTS.md` e registrar como `legacy-known`
- parar se o problema depender de ambiente/banco inacessivel e registrar como
  `environment`
