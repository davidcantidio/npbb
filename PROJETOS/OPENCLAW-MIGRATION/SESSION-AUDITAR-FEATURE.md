---
doc_id: "SESSION-AUDITAR-FEATURE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OPENCLAW-MIGRATION"
---

# SESSION-AUDITAR-FEATURE - Auditoria de Feature em Sessao de Chat

## Objetivo

Auditar a feature atualmente pronta para gate em `OPENCLAW-MIGRATION` usando a
estrutura canonica sob `features/`.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`

## Parametros Preenchidos

```text
PROJETO:       OPENCLAW-MIGRATION
FEATURE_ID:    <resolver_na_feature_pronta_para_gate>
FEATURE_PATH:  <resolver_na_feature_pronta_para_gate>
RODADA:        <resolver_na_feature_pronta_para_gate>
BASE_COMMIT:   worktree
AUDIT_LOG:     /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/PROJETOS/OPENCLAW-MIGRATION/AUDIT-LOG.md
```

## Regra Local Adicional

- descubra a feature pronta para auditoria a partir de
  `PROJETOS/OPENCLAW-MIGRATION/features/FEATURE-*/FEATURE-*.md`
- trate qualquer referencia residual a `FASE` no `AUDIT-LOG.md` apenas como
  compatibilidade historica
- a sessao nao deve reabrir fluxo `ISSUE/FASE`

