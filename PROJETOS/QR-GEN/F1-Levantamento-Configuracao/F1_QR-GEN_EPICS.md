---
doc_id: "F1_QR-GEN_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "pending"
---

# Epicos - QR-GEN / F1 - Levantamento e Configuracao

## Objetivo da Fase

Confirmar estado atual e garantir configuracao de producao. Levantar volume de registros `ativacao` com URL incorreta e documentar obrigatoriedade de `PUBLIC_APP_BASE_URL` em producao.

## Gate de Saida da Fase

- Volume de registros incorretos documentado
- PM e DevOps cientes da dependencia de configuracao

## Estado do Gate de Auditoria

- gate_atual: `pending`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [x] todos os epicos estao `done`
- [x] todas as issues filhas estao `done`
- [x] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Levantamento | Script/query para contar ativacao com localhost | nenhuma | done | [EPIC-F1-01-Levantamento.md](./EPIC-F1-01-Levantamento.md) |
| EPIC-F1-02 | Documentacao | Documentar PUBLIC_APP_BASE_URL e checklist deploy | EPIC-F1-01 | done | [EPIC-F1-02-Documentacao.md](./EPIC-F1-02-Documentacao.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma
- `EPIC-F1-02`: depende de EPIC-F1-01 (volume documentado informa prioridade)

## Escopo desta Fase

### Dentro
- Script ou query para contar `ativacao` com `landing_url` ou `url_promotor` contendo `localhost` ou `127.0.0.1`
- Documentacao em `docs/SETUP.md` e/ou `docs/DEPLOY_*.md` sobre obrigatoriedade de `PUBLIC_APP_BASE_URL` em producao
- Checklist de deploy para `app.npbb.com.br` incluindo verificacao dessa variavel

### Fora
- Migracao de dados (F2)
- Safeguards em runtime (F3)
- Suporte a staging/homologacao

## Definition of Done da Fase
- [x] Volume de registros incorretos documentado
- [x] Documentacao de configuracao em producao publicada
- [x] Checklist de deploy criado e revisado
