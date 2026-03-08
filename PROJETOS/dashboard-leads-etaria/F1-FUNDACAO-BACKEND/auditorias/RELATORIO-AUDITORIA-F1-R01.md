---
doc_id: "RELATORIO-AUDITORIA-F1-R01.md"
version: "1.1"
status: "provisional"
verdict: "cancelled"
scope_type: "phase"
scope_ref: "F1-FUNDACAO-BACKEND"
phase: "F1"
reviewer_model: "GPT-5 Codex"
base_commit: "c0a31d29ebe4b949229706daa1f84888ae8bca44"
compares_to: "none"
round: 1
supersedes: "none"
followup_destination: "cancelled"
last_updated: "2026-03-08"
---

# RELATORIO-AUDITORIA - DASHBOARD-LEADS-ETARIA / F1 - FUNDACAO-BACKEND / R01

## Resumo Executivo

A fase F1 apresenta aderencia funcional ao intake e ao PRD no escopo auditado: os testes
de servico e endpoint da analise etaria passaram e cobrem limites de faixa etaria,
cobertura BB, filtros, consolidado, autenticacao e contrato OpenAPI.

Esta rodada nao pode aprovar o gate da fase porque o worktree estava sujo durante a
auditoria. Conforme `AUDITORIA-GOV.md`, o resultado precisa permanecer `provisional` e o
veredito da rodada fica `cancelled`.

## Escopo Auditado e Evidencias

- intake: `PROJETOS/dashboard-leads-etaria/INTAKE-DASHBOARD-LEADS-ETARIA.md`
- prd: `PROJETOS/dashboard-leads-etaria/PRD-DASHBOARD-LEADS-ETARIA.md`
- fase: `PROJETOS/dashboard-leads-etaria/F1-FUNDACAO-BACKEND/F1_DASHBOARD_LEADS_ETARIA_EPICS.md`
- epicos:
  - `PROJETOS/dashboard-leads-etaria/F1-FUNDACAO-BACKEND/EPIC-F1-01-EXTENSAO-MODELO-LEAD.md`
  - `PROJETOS/dashboard-leads-etaria/F1-FUNDACAO-BACKEND/EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md`
- issues: todas as issues de `PROJETOS/dashboard-leads-etaria/F1-FUNDACAO-BACKEND/issues/`
- testes:
  - `cd backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_service.py tests/test_dashboard_age_analysis_endpoint.py`
  - resultado observado: `13 passed in 5.81s`
- diff/commit:
  - commit base auditado: `c0a31d29ebe4b949229706daa1f84888ae8bca44`
  - evidência operacional: `git status --short --untracked-files=normal` retornou árvore suja com alterações fora do escopo da F1

## Conformidades

- `backend/tests/test_dashboard_age_analysis_service.py` valida limites 17, 18, 25, 26, 40 e 41 para `calculate_age` e `classify_age_range`.
- `backend/tests/test_dashboard_age_analysis_endpoint.py` cobre ausência de `data_nascimento`, threshold de cobertura BB, consolidado com Top 3, média, mediana, filtro por `evento_id`, base vazia e `401` sem autenticação.
- O contrato OpenAPI do endpoint `/dashboard/leads/analise-etaria` está coberto por teste dedicado.
- Não foram observados achados materiais de bug, regressão provável ou drift arquitetural no escopo backend auditado.

## Nao Conformidades

- A rodada não atende o pré-requisito de árvore limpa para auditoria formal. Isso impede veredito `go` e fechamento do gate da fase nesta execução.

## Saude Estrutural do Codigo

| ID | Categoria | Severidade | Componente | Descricao | Evidencia | Impacto | Bloqueante? | Destino sugerido |
|---|---|---|---|---|---|---|---|---|
| n-a | n-a | n-a | escopo F1 auditado | Nenhum achado material de saude estrutural foi identificado na amostragem do backend do dashboard. | Testes de servico e endpoint passaram sem falhas. | Sem impacto adicional identificado. | nao | cancelled |

## Bugs e Riscos Antecipados

| ID | Categoria | Severidade | Descricao | Evidencia | Correcao sugerida | Bloqueante? |
|---|---|---|---|---|---|---|
| A-01 | scope-drift | low | A fase não pode ser encerrada enquanto a auditoria formal continuar sendo executada sobre worktree sujo. | `git status --short --untracked-files=normal` retornou alterações modificadas e não rastreadas fora do escopo auditado. | Reexecutar a auditoria da F1 em árvore limpa, no mesmo commit base ou sucessor equivalente. | sim |

## Cobertura de Testes

| Funcionalidade | Teste existe? | Tipo | Observacao |
|---|---|---|---|
| Limites de faixa etaria e idade calculada | sim | unitario | `test_dashboard_age_analysis_service.py` cobre 17, 18, 25, 26, 40 e 41 |
| Serializacao do contrato tipado | sim | unitario | `test_age_analysis_response_serialization` valida o envelope de resposta |
| Cobertura BB, consolidado e filtros | sim | integracao | `test_dashboard_age_analysis_ok` e testes correlatos cobrem payload e agregacoes |
| Base vazia e autenticacao | sim | integracao | `test_dashboard_age_analysis_empty_response` e `test_dashboard_age_analysis_requires_auth` |
| OpenAPI do endpoint | sim | contrato | `test_dashboard_age_analysis_openapi_contract` |

## Decisao

- veredito: `cancelled`
- justificativa: a amostragem técnica do escopo F1 não revelou achados materiais bloqueantes, mas a auditoria formal não pode aprovar gate com worktree sujo
- gate_da_fase: `pending`
- follow_up_destino_padrao: `cancelled`

## Handoff para Novo Intake

> Nao se aplica a esta rodada.

- nome_sugerido_do_intake: n-a
- intake_kind_recomendado: n-a
- problema_resumido: n-a
- evidencias: n-a
- impacto: n-a
- escopo_presumido: n-a

## Follow-ups Bloqueantes

1. Reexecutar a auditoria formal da F1 com a árvore limpa para permitir veredito válido e fechamento do gate.

## Follow-ups Nao Bloqueantes

1. Nenhum follow-up técnico adicional foi aberto nesta rodada.
