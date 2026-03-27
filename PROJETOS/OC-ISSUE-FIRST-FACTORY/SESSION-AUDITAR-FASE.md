---
doc_id: "SESSION-AUDITAR-FASE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OC-ISSUE-FIRST-FACTORY"
---

# SESSION-AUDITAR-FASE - Auditoria de Fase em Sessao de Chat

## Objetivo

Auditar a fase atualmente pronta para gate, conforme manifesto da fase e `AUDIT-LOG.md`.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`

## Parametros Preenchidos

```text
PROJETO:      OC-ISSUE-FIRST-FACTORY
FASE:         <resolver_na_fase_pronta_para_gate>
RODADA:       <resolver_na_fase_pronta_para_gate>
BASE_COMMIT:  <resolver_na_fase_pronta_para_gate>
AUDIT_LOG:    PROJETOS/OC-ISSUE-FIRST-FACTORY/AUDIT-LOG.md
```

## Regra Local Adicional

- descubra a fase pronta para auditoria a partir de `AUDIT-LOG.md` e dos manifestos `F*_EPICS.md`
- nao congele este wrapper na fase bootstrap; use a rodada correspondente ao estado atual do projeto
- o log do projeto permanece em `PROJETOS/OC-ISSUE-FIRST-FACTORY/AUDIT-LOG.md`
