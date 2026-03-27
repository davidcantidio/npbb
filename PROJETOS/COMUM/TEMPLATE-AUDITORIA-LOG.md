---
doc_id: "AUDIT-LOG.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "YYYY-MM-DD"
---

# AUDIT-LOG - <PROJETO>

## Politica

- toda auditoria formal deve gerar relatorio versionado por feature em `auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `same-feature`, `new-intake` ou `cancelled`
- `issue-local` pode aparecer apenas como enum legado de compatibilidade
- auditoria `go` e pre-requisito para mover feature a `features/encerradas/`
- cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada
  `hold` que gerou o item

## Gate Atual por Feature

| Feature | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| preencher |  |  |  |  |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Feature | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | FEATURE-1-R01 | FEATURE-1 | B1 | same-feature | resumo curto | US-1-03-CORRECAO/README.md | bloqueante |

> Em `Ref`, para `same-feature`, apontar para a pasta `US-*/` ou para o
> `README.md` correspondente. Se o projeto ainda carregar follow-up legado como
> `issue-local`, manter a referencia historica sem promovê-la a contrato novo.

## Rodadas

| Audit ID | Feature | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
