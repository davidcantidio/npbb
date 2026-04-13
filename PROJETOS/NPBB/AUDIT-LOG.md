---
doc_id: "AUDIT-LOG.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-04-13"
---

# AUDIT-LOG - NPBB

## Politica

- toda auditoria formal deve gerar relatorio versionado por feature em `features/FEATURE-*/auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `same-feature`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para encerrar a feature
- cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada `hold` que gerou o item

## Gate Atual por Feature

| Feature | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| [FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md) | approved | FEATURE-1-R01 | [RELATORIO-AUDITORIA-F1-R01.md](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | R01 aprovada em `2026-04-12`; `DRIFT_INDICE` registrado por preflight `exit 12`; nenhum follow-up bloqueante; projeto apto para encerramento. |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Feature | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - |

## Rodadas

| Audit ID | Feature | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FEATURE-1-R01 | FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD | 2026-04-12 | gpt-5-codex | d1414d0c288eeb0be8364658cc41962d51d9b283 | - | go | done | [RELATORIO-AUDITORIA-F1-R01.md](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | `M-01` e `M-02` em warn nao bloqueante; limitacao ETL sem `batch_id` mantida documentada | - | - | - |

## Integracao pos-auditoria (operacional, 2026-04-13)

- **Branch auditada:** `audit/feature1-r01` publicada em `origin`; **tronco `main`:** fast-forward primeiro ate `23c8ff48521ea90c79b71ba1a2e6d5c1e93a0ebd` (artefatos finais R01), depois commits de trilha pos-R01 (governanca, timeouts Vitest em suites pesadas, alinhamento do registo). **Tip de `main`:** apos `git fetch`, usar `git rev-parse origin/main`; a **linha de base auditada (R01)** permanece `23c8ff48521ea90c79b71ba1a2e6d5c1e93a0ebd`. Integracao executada a partir de worktree limpo (sem usar o clone principal sujo como fonte de merge).
- **Verificacao pos-merge (subset R01):** `npm run typecheck`; `npm run test -- ImportacaoPage.test.tsx LegacyLeadStepRedirect.test.tsx MapeamentoPage.test.tsx PipelineStatusPage.test.tsx --run` (18 passed); `pytest tests/test_lead_gold_pipeline.py tests/test_lead_silver_mapping.py` com `TESTING=true` e `PYTHONPATH` conforme [`AGENTS.md`](../../AGENTS.md) (31 passed nesta sessao).
- **`DRIFT_INDICE` (R01):** o registo de `2026-04-12` no relatorio R01 **mantem-se** (preflight exit 12; `FABRICA_PROJECTS_DATABASE_URL` ausente). **Resolucao quando o Postgres estiver disponivel:** seguir `PROJETOS/COMUM/SPEC-RUNTIME-POSTGRES-MATRIX.md` (preflight `ensure-fabrica-projects-index-runtime.sh`, bootstrap se necessario, `sync-fabrica-projects-db.sh` ou `fabrica.py sync` conforme ambiente); apos sync com sucesso, acrescentar **nova** linha nesta secao com data da operacao e SHA do repo sincronizado — **nao** reescrever corpo datado de `RELATORIO-AUDITORIA-F1-R01.md`.
