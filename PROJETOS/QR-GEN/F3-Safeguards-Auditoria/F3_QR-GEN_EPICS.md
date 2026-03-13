---
doc_id: "F3_QR-GEN_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "not_ready"
---

# Epicos - QR-GEN / F3 - Safeguards e Auditoria

## Objetivo da Fase

Reduzir risco de regressao futura. Guard em `hydrate_ativacao_public_urls` ou no fluxo de persistencia que detecte URL local em ambiente de producao.

## Gate de Saida da Fase

- Regressao detectavel em CI ou em runtime em producao
- Teste automatizado cobrindo cenario producao vs dev

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F3-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F3-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Safeguards | Guard em producao + teste automatizado | F2 concluida | todo | [EPIC-F3-01-Safeguards.md](./EPIC-F3-01-Safeguards.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: F2 concluida (migracao e validacao)

## Escopo desta Fase

### Dentro
- Guard em `hydrate_ativacao_public_urls` ou no fluxo de persistencia que levante erro ou warning quando, em ambiente de producao, a URL calculada contiver host local
- Teste automatizado cobrindo cenario producao vs dev

### Fora
- Suporte a staging/homologacao
- Alteracao da logica de renderizacao do QR no frontend

## Definition of Done da Fase
- [ ] Guard implementado e testado
- [ ] Regressao detectavel em CI ou runtime em producao
