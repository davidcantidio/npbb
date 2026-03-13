---
doc_id: "EPIC-F2-01-Migracao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F2-01 - Migracao

## Objetivo

Criar script de migracao que identifica `ativacao` com `landing_url`/`url_promotor` contendo host local, recalcula `landing_url` e `qr_code_url` usando `PUBLIC_APP_BASE_URL`, e atualiza os registros. Script idempotente com dry-run.

## Resultado de Negocio Mensuravel

Registros existentes com URL incorreta corrigidos; zero QR codes com URL local persistidos no banco.

## Contexto Arquitetural

- `backend/app/utils/urls.py` — `get_public_app_base_url()`, `build_ativacao_public_urls()`
- `backend/app/services/landing_pages.py` — `hydrate_ativacao_public_urls()`
- Tabela `ativacao` — colunas `landing_url`, `qr_code_url`, `url_promotor`

## Definition of Done do Epico
- [ ] Script de migracao executavel e testado
- [ ] Dry-run e idempotencia validados
- [ ] Rollback documentado

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Script Migracao Ativacao URL | Migracao que identifica, recalcula e atualiza `ativacao` | 5 | todo | [ISSUE-F2-01-001-Script-Migracao-Ativacao-Url.md](./issues/ISSUE-F2-01-001-Script-Migracao-Ativacao-Url.md) |
| ISSUE-F2-01-002 | Idempotencia Dry-Run Migracao | Garantir idempotencia e dry-run no script | 2 | todo | [ISSUE-F2-01-002-Idempotencia-Dry-Run-Migracao.md](./issues/ISSUE-F2-01-002-Idempotencia-Dry-Run-Migracao.md) |

## Artifact Minimo do Epico

- Script de migracao em `backend/alembic/versions/` ou `backend/scripts/`
- Documentacao de uso, dry-run e rollback

## Dependencias

- [Intake](../INTAKE.md)
- [PRD](../PRD-QR-GEN.md)
- [Fase](./F2_QR-GEN_EPICS.md)
- [F1](../F1-Levantamento-Configuracao/F1_QR-GEN_EPICS.md) — concluida
