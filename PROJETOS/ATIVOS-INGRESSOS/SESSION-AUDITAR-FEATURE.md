---
doc_id: "SESSION-AUDITAR-FEATURE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
---

# SESSION-AUDITAR-FEATURE - Auditoria de Feature em Sessao de Chat

## Objetivo

Auditar a feature atualmente pronta para gate, conforme manifesto da feature e `AUDIT-LOG.md`.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`

## Parametros Preenchidos

```text
PROJETO:       ATIVOS-INGRESSOS
FEATURE_ID:    <resolver_na_feature_pronta_para_gate>
FEATURE_PATH:  <resolver_na_feature_pronta_para_gate>
RODADA:        <resolver_na_feature_pronta_para_gate>
BASE_COMMIT:   worktree
AUDIT_LOG:     PROJETOS/ATIVOS-INGRESSOS/AUDIT-LOG.md
```

## Regra Local Adicional

- descubra a feature pronta para auditoria a partir de `AUDIT-LOG.md` e dos manifestos `FEATURE-*.md`
- nao congele este wrapper na bootstrap; use a rodada correspondente ao estado atual do projeto
- o log do projeto permanece em `PROJETOS/ATIVOS-INGRESSOS/AUDIT-LOG.md`
