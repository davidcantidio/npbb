---
doc_id: "F2_QR-GEN_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "not_ready"
---

# Epicos - QR-GEN / F2 - Migracao de Dados e Validacao

## Objetivo da Fase

Corrigir registros existentes com URL incorreta. Script de migracao idempotente com dry-run e validacao pos-migracao.

## Gate de Saida da Fase

- Migracao executada com sucesso em ambiente alvo
- Metrica: zero QR codes com URL de localhost persistidos no banco

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
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Migracao | Script de migracao idempotente com dry-run | F1 concluida | todo | [EPIC-F2-01-Migracao.md](./EPIC-F2-01-Migracao.md) |
| EPIC-F2-02 | Validacao | Teste de validacao pos-migracao (zero localhost) | EPIC-F2-01 | todo | [EPIC-F2-02-Validacao.md](./EPIC-F2-02-Validacao.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: F1 concluida (levantamento e documentacao)
- `EPIC-F2-02`: depende de EPIC-F2-01 (migracao executada)

## Escopo desta Fase

### Dentro
- Script de migracao (Alembic data migration ou standalone) que identifica, recalcula e atualiza `ativacao` com URL local
- Script idempotente e com dry-run
- Testes de validacao: zero registros com localhost apos migracao

### Fora
- Safeguards em runtime (F3)
- Suporte a staging/homologacao
- Alteracao da logica de renderizacao do QR no frontend

## Definition of Done da Fase
- [ ] Migracao executada com sucesso em ambiente alvo
- [ ] Zero registros com localhost no banco apos migracao
- [ ] Script com dry-run e idempotencia validados
