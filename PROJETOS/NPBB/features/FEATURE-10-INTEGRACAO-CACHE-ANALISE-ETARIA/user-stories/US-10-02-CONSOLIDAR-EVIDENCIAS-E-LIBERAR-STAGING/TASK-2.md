---
doc_id: "TASK-2.md"
user_story_id: "US-10-02-CONSOLIDAR-EVIDENCIAS-E-LIBERAR-STAGING"
task_id: "T2"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "artifacts/phase-f4/evidence/"
  - "PROJETOS/NPBB/features/FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA/**"
  - "docs/SETUP.md"
  - "render.yaml"
tdd_aplicavel: false
---

# T2 - Rodar gate final e emitir decisao de staging

## objetivo

Executar o gate final do repo, consolidar checklist de staging e emitir um
resumo PASS/FAIL que separe regressao nova de legado conhecido.

## precondicoes

- `T1` concluida com evidencias minimas salvas
- comandos de frontend e backend aptos a rodar no ambiente local
- baseline de legados conhecidos lida em `AGENTS.md`

## orquestracao

- `depends_on`: `T1`
- `parallel_safe`: `false`
- `write_scope`: evidencias e governanca da feature

## arquivos_a_ler_ou_tocar

- `Makefile`
- `docs/SETUP.md`
- `render.yaml`
- `artifacts/phase-f4/evidence/`
- `PROJETOS/NPBB/features/FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA/**`

## passos_atomicos

1. tentar `make ci-quality`
2. classificar cada falha remanescente em `regression`, `legacy-known` ou
   `environment`
3. preencher checklist de staging e notas de rollback
4. registrar a decisao final: `pronto para staging` ou `bloqueado`
5. anexar comandos executados, limites e pendencias no resumo final

## comandos_permitidos

- `make ci-quality`
- `cd backend && python scripts/verify_leads_runtime_env.py --service api`
- `cd backend && python scripts/verify_leads_runtime_env.py --service worker`
- `cd backend && python scripts/verify_leads_hardening_db.py`

## resultado_esperado

Resumo objetivo da rodada com gate tentado, evidencias referenciadas, notas de
rollback e decisao explicita de staging.

## testes_ou_validacoes_obrigatorias

- `make ci-quality`
- classificacao formal de falhas do gate
- checklist de staging preenchido
- notas de rollback registradas

## stop_conditions

- parar se houver regressao nova sem correcao na trilha do cache etario
- parar se o gate nao puder ser tentado e registrar claramente o motivo
- parar se a liberacao depender de mudança fora do escopo desta feature
