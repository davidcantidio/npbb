---
doc_id: "EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F4 CICD e Limpeza - Epicos

## Objetivo da Fase

Automatizar o deploy pos-migracao para a VPS Hostinger, garantir backup diario com restore validado e eliminar dependencias legadas de Render, Supabase e Wrangler antes da decisao final de promocao.

## Gate de Saida da Fase

`make eval-integrations: PASS`, `make ci-quality: PASS`, ultimo backup diario gera dump local e copia no volume externo, Render e Supabase estao pausados, e `artifacts/phase-f4/validation-summary.md` registra decisao `promote`.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F4-01` | Pipeline Deploy SSH | Automatizar build, sincronizacao de artefatos e deploy remoto auditavel por SSH | `todo` | [EPIC-F4-01-PIPELINE-DEPLOY-SSH.md](./EPIC-F4-01-PIPELINE-DEPLOY-SSH.md) |
| `EPIC-F4-02` | Backup Automatizado | Garantir dump diario, retencao 7+4, copia externa e restore drill <= 30 min | `todo` | [EPIC-F4-02-BACKUP-AUTOMATIZADO.md](./EPIC-F4-02-BACKUP-AUTOMATIZADO.md) |
| `EPIC-F4-03` | Coerencia Normativa e Gate | Bloquear legado residual, validar saude pos-cutover e consolidar decisao promote | `todo` | [EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md](./EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md) |

## Escopo desta Entrega

Inclui workflow de deploy por SSH em `main`, publicacao do `dist/` na VPS, backup com retencao e restore drill, criacao dos gates `make`, arquivamento de artefatos legados e geracao do summary final; exclui reprovisionamento da VPS, dump/restore inicial do banco e redesenho de Nginx/TLS ja pertencentes a F1-F3.
