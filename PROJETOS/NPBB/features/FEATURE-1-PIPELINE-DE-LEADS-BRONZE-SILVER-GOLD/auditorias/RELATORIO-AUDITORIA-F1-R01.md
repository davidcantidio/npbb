---
doc_id: "RELATORIO-AUDITORIA-F1-R01"
version: "1.0"
status: "planned"
scope_type: "feature"
scope_ref: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
feature_id: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
reviewer_model: "nao_aplicavel"
base_commit: "HEAD"
compares_to: "none"
round: 1
supersedes: "none"
followup_destination: "same-feature"
decision_refs: []
last_updated: "2026-03-26"
---

# RELATORIO-AUDITORIA - NPBB / FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD / R01

## Resumo Executivo

Este ficheiro e um shell para a primeira rodada de auditoria da feature.
Com `status: planned`, a rodada nao foi executada; o `AUDIT-LOG.md`
permanece sem veredito material ate haver auditoria real.

## Escopo Auditado e Evidencias

- intake: [INTAKE-NPBB.md](../../../INTAKE-NPBB.md)
- prd: [PRD-NPBB.md](../../../PRD-NPBB.md)
- feature: [Feature piloto](../FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
- user stories: [US piloto](../user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md)
- testes: `tests/test_criar_projeto.py`, `tests/test_fabrica_boundary.py`
- diff/commit: nao aplicavel ainda

## Conformidades

- nao aplicavel enquanto `planned`

## Nao Conformidades

- nao aplicavel enquanto `planned`

## Cobertura de Testes

| Funcionalidade | Teste existe? | Tipo | Observacao |
|---|---|---|---|
| governanca do projeto | sim | unit | cobre scaffold, wrappers canonicos e indice derivado |

## Decisao

- estado do artefato: `planned`
- veredito canonico (`go` / `hold` / `cancelled`): nao aplicavel ate conclusao da rodada
- gate_da_feature: `not_ready`
- follow-up padrao: `same-feature`

## Follow-ups Bloqueantes

1. nao aplicavel ao shell `planned`

## Follow-ups Nao Bloqueantes

1. nao aplicavel ao shell `planned`
