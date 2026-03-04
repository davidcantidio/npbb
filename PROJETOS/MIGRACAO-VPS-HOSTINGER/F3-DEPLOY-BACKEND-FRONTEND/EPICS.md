---
doc_id: "PHASE-F3-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F3 Deploy Backend e Frontend - Epicos

## Objetivo da Fase

Colocar `api`, `web` e `edge` operacionais na VPS Hostinger, primeiro por IP para homologacao e depois por dominio HTTPS, consumindo o Postgres local ja migrado na F2 e removendo a dependencia operacional de Render e Cloudflare Pages.

## Gate de Saida da Fase

`./scripts/deploy_vps.sh /opt/npbb/env/.env.production` e `./scripts/smoke_vps.sh /opt/npbb/env/.env.production` passam com `DEPLOY_MODE=domain` e `ENABLE_TLS=true`; `https://${API_DOMAIN}/health` responde `200`; `https://${API_DOMAIN}/auth/me` e `https://${API_DOMAIN}/leads?page=1&page_size=10` respondem `200` com latencia `< 500ms`; `https://${APP_DOMAIN}/`, `https://${APP_DOMAIN}/eventos` e `https://${APP_DOMAIN}/leads` servem a SPA corretamente.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F3-01` | Deploy Backend VPS | Subir o backend FastAPI na VPS contra o Postgres local com contrato de env, healthchecks e smoke autenticado. | `todo` | [EPIC-F3-01-DEPLOY-BACKEND-VPS.md](./EPIC-F3-01-DEPLOY-BACKEND-VPS.md) |
| `EPIC-F3-02` | Deploy Frontend Nginx | Publicar o frontend estatico e o edge Nginx em modo IP e dominio, preservando SPA fallback e proxy correto. | `todo` | [EPIC-F3-02-DEPLOY-FRONTEND-NGINX.md](./EPIC-F3-02-DEPLOY-FRONTEND-NGINX.md) |
| `EPIC-F3-03` | TLS e DNS Cutover | Executar o cutover HTTPS com Cloudflare DNS-only e Let's Encrypt, com latencia medida e rollback claro. | `todo` | [EPIC-F3-03-TLS-E-DNS-CUTOVER.md](./EPIC-F3-03-TLS-E-DNS-CUTOVER.md) |

## Escopo desta Entrega

Inclui deploy por IP, build do frontend, configuracao do edge, smoke operacional, cutover HTTPS e rollback com nomenclatura explicita entre PRD e implementacao real do repositorio (`postgres=db`, `api=backend`, `web=frontend`, `edge=nginx`). Exclui CI/CD automatico, backup automatizado e limpeza final de `.wrangler/` e `render.yaml`, que permanecem na F4.
