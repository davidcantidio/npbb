---
doc_id: "PHASE-F1-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F1 Preparacao Infra - Epicos

## Objetivo da Fase

Padronizar e validar a stack Hostinger em modo IP, com bootstrap idempotente, contrato de ambiente auditavel e stack `postgres`, `api`, `web`, `edge` e `backup` pronta para subir na VPS com smoke HTTP verde.

## Gate de Saida da Fase

`./scripts/deploy_vps.sh /opt/npbb/env/.env.production` conclui sem erro na VPS, `docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml ps` mostra `postgres`, `api`, `web`, `edge` e `backup` saudaveis/operacionais conforme o contrato da stack, e `./scripts/smoke_vps.sh /opt/npbb/env/.env.production` passa em modo IP para `/api/health`, `/api/docs`, `/`, `/eventos` e smoke de autenticacao invalida.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F1-01` | Provisionamento VPS | Entregar bootstrap idempotente da VPS, baseline de hardening e contrato de ambiente para deploy Hostinger. | `todo` | [EPIC-F1-01-PROVISIONAMENTO-VPS.md](./EPIC-F1-01-PROVISIONAMENTO-VPS.md) |
| `EPIC-F1-02` | Docker Compose e Nginx | Fechar o contrato operacional da stack `postgres/api/web/edge/backup`, da renderizacao Nginx em modo IP e dos smokes da fase. | `todo` | [EPIC-F1-02-DOCKER-COMPOSE-E-NGINX.md](./EPIC-F1-02-DOCKER-COMPOSE-E-NGINX.md) |

## Escopo desta Entrega

Inclui bootstrap da VPS, usuario nao-root, SSH por chave, `ufw`, `fail2ban`, contrato de `.env`, preflight de deploy, auditoria do `docker-compose`, Nginx em modo IP e smoke operacional. Exclui restore do banco Supabase, `pg_restore`, cutover DNS, TLS final, Cloudflare, remocao de `render.yaml`, remocao de `.wrangler` e deploy automatico via GitHub Actions.
