---
doc_id: "EPIC-F3-02-DEPLOY-FRONTEND-NGINX"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F3-02 - Deploy Frontend Nginx

## Objetivo

Publicar o frontend via `web` e o edge via `edge`, com build consistente para os modos IP e dominio, SPA fallback preservado e proxy correto entre browser, edge e API.

## Resultado de Negocio Mensuravel

O usuario passa a acessar a interface principal direto da VPS, sem Cloudflare Pages ou Wrangler, com roteamento previsivel e uma unica borda HTTP controlada pelo projeto.

## Definition of Done

- O build do frontend respeita `VITE_API_BASE_URL` em modo IP e em modo dominio.
- `frontend/nginx.conf` continua garantindo SPA fallback.
- Os templates do `edge` rendem corretamente `ip.conf`, `app.conf`, `api.conf`, `app-tls.conf` e `api-tls.conf`.
- O smoke da fase cobre `/`, `/eventos` e `/leads` pelo edge publicado.

## Issues

### ISSUE-F3-02-01 - Garantir build do frontend para modo IP e modo dominio
Status: todo

**User story**
Como pessoa responsavel pelo frontend em producao, quero que o build estatico aponte para a API correta tanto na homologacao por IP quanto no cutover por dominio para evitar requests quebrados apos o deploy.

**Plano TDD**
1. `Red`: ampliar `frontend/e2e/auth-session.smoke.spec.ts` e `frontend/e2e/internal-architecture.api.smoke.spec.ts`, e criar `tests/test_frontend_vps_env_contract.py`, para falhar quando o build em `frontend/Dockerfile` nao respeitar `VITE_API_BASE_URL`, `API_ROOT_PATH` e `COOKIE_SECURE` nos dois modos.
2. `Green`: alinhar `frontend/Dockerfile`, `Infra/production/.env.example` e `docs/DEPLOY_HOSTINGER_VPS.md` para os modos `ip` e `domain`.
3. `Refactor`: consolidar no texto do epico e nos docs operacionais a matriz de envs obrigatorias por modo.

**Criterios de aceitacao**
- Given `DEPLOY_MODE=ip`, When o frontend e buildado, Then ele consome `http://<ip-publico>/api` e carrega `/leads` sem quebrar navegacao.
- Given `DEPLOY_MODE=domain`, When o frontend e buildado, Then ele consome `https://${API_DOMAIN}` com `COOKIE_SECURE=true` e sem prefixo `/api`.

### ISSUE-F3-02-02 - Fechar templates do edge e roteamento entre `web` e `api`
Status: todo

**User story**
Como pessoa responsavel pela borda HTTP, quero que os templates do Nginx gerem a configuracao correta para IP, dominio sem TLS e dominio com TLS para que o roteamento seja deterministico em qualquer etapa da migracao.

**Plano TDD**
1. `Red`: criar `tests/test_nginx_render_templates.py` para inspecionar `Infra/production/nginx/render.sh`, `Infra/production/nginx/conf.d/ip.conf.template`, `Infra/production/nginx/conf.d/app.conf.template`, `Infra/production/nginx/conf.d/api.conf.template`, `Infra/production/nginx/conf.d/app.tls.conf.template` e `Infra/production/nginx/conf.d/api.tls.conf.template`, falhando se a selecao dos arquivos ou os headers de proxy ficarem inconsistentes.
2. `Green`: corrigir `Infra/production/nginx/render.sh`, os templates em `Infra/production/nginx/conf.d/` e, se necessario, `Infra/production/nginx/nginx.conf`.
3. `Refactor`: reduzir duplicacao entre as configuracoes `ip` e `domain`, mantendo apenas o que muda de fato por host e TLS.

**Criterios de aceitacao**
- Given `DEPLOY_MODE=ip`, When o `edge` renderiza a configuracao, Then `/api/*` vai para `api:8000` e `/` vai para `web:80`.
- Given `DEPLOY_MODE=domain` com `ENABLE_TLS=true`, When o `edge` renderiza a configuracao, Then os vhosts de `APP_DOMAIN` e `API_DOMAIN` usam os arquivos de certificado esperados e preservam os headers `X-Forwarded-*`.

### ISSUE-F3-02-03 - Validar smoke das rotas SPA e docs pelo edge publicado
Status: todo

**User story**
Como pessoa que homologa a aplicacao na borda, quero smoke funcional das rotas publicas e da documentacao da API para garantir que o publish da camada web nao introduziu regressao de roteamento.

**Plano TDD**
1. `Red`: ampliar `scripts/smoke_vps.sh`, `frontend/nginx.conf`, `frontend/e2e/auth-session.smoke.spec.ts` e `frontend/e2e/internal-architecture.api.smoke.spec.ts` para falhar quando `/`, `/eventos`, `/leads` ou `docs` deixarem de responder pela borda publicada.
2. `Green`: ajustar `scripts/smoke_vps.sh` e `docs/DEPLOY_HOSTINGER_VPS.md` para refletir o smoke completo do edge.
3. `Refactor`: centralizar em `scripts/smoke_vps.sh` as URLs publicas derivadas de `PUBLIC_APP_BASE_URL` e `PUBLIC_API_DOC_URL`.

**Criterios de aceitacao**
- Given a stack publicada por IP ou dominio, When `./scripts/smoke_vps.sh` roda, Then `GET /`, `GET /eventos` e `GET /leads` retornam a SPA com `id="root"`.
- Given a API publicada no edge, When `GET ${PUBLIC_API_DOC_URL}` roda, Then o Swagger responde `200` e contem `Swagger UI`.

## Artifact Minimo do Epico

- `artifacts/phase-f3/epic-f3-02-deploy-frontend-nginx.md` com evidencias do build, do roteamento do edge e da cobertura de smoke das rotas publicas.

## Dependencias

- [PRD](../prd_vps_migration.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
