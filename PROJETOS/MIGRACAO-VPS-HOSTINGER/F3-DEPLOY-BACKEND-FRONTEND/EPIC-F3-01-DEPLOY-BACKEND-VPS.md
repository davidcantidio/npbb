---
doc_id: "EPIC-F3-01-DEPLOY-BACKEND-VPS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F3-01 - Deploy Backend VPS

## Objetivo

Colocar o servico `api` saudavel na VPS, apontando para `postgres` local, com contrato de ambiente auditavel, migrations aplicadas e smoke autenticado dos endpoints criticos.

## Resultado de Negocio Mensuravel

O backend passa a responder na Hostinger sem cold start e com banco local, reduzindo latencia e removendo a dependencia operacional do Render.

## Definition of Done

- `postgres` e `api` sobem via Compose com `restart: unless-stopped` e healthchecks validos.
- `scripts/deploy_vps.sh` falha antes do `up` se variaveis criticas do backend estiverem ausentes.
- `scripts/smoke_vps.sh` valida `health`, `docs`, `auth/me` e `leads` com credenciais reais quando disponiveis.
- O texto do epico amarra o deploy ao banco local ja restaurado na F2, sem reabrir escopo de migracao de dados.

## Issues

### ISSUE-F3-01-01 - Fechar contrato Compose e env do backend na VPS
Status: todo

**User story**
Como pessoa responsavel pelo deploy do backend, quero um contrato de Compose e de ambiente verificavel para evitar subir a API na VPS com configuracao incompleta ou apontando para a infraestrutura legada.

**Plano TDD**
1. `Red`: criar `tests/test_vps_compose_contract.py` para inspecionar `Infra/production/docker-compose.yml`, `Infra/production/.env.example` e `scripts/deploy_vps.sh`, falhando se `postgres` ou `api` nao tiverem `healthcheck`, `restart: unless-stopped` e envs obrigatorias.
2. `Green`: ajustar `Infra/production/docker-compose.yml`, `Infra/production/.env.example` e `scripts/deploy_vps.sh` para fechar o contrato do backend contra o Postgres local.
3. `Refactor`: padronizar a terminologia em `docs/DEPLOY_HOSTINGER_VPS.md` para deixar explicito o mapeamento PRD `backend/db` para repo `api/postgres`.

**Criterios de aceitacao**
- Given um `.env.production` sem `DATABASE_URL`, `DIRECT_URL`, `SECRET_KEY` ou `FRONTEND_ORIGIN`, When `./scripts/deploy_vps.sh` roda, Then o deploy falha antes de subir containers.
- Given um `.env.production` valido, When `docker compose config` e `docker compose up -d postgres api` sao executados pelo script, Then ambos os servicos ficam aptos a `healthy`.

### ISSUE-F3-01-02 - Validar boot do backend com smoke autenticado de `/auth/me` e `/leads`
Status: todo

**User story**
Como pessoa que homologa a API na VPS, quero smoke autentico dos endpoints criticos para garantir que a aplicacao esta funcional antes de qualquer cutover de dominio.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_auth_login.py` e `backend/tests/test_leads_list_endpoint.py`, e criar `tests/test_smoke_vps_script.py`, para falhar quando `scripts/smoke_vps.sh` nao verificar `GET /auth/me` e `GET /leads?page=1&page_size=10`.
2. `Green`: atualizar `scripts/smoke_vps.sh` e `docs/DEPLOY_HOSTINGER_VPS.md` para exigir e documentar esse smoke autenticado.
3. `Refactor`: centralizar em `scripts/smoke_vps.sh` a obtencao de token e a derivacao da base URL da API.

**Criterios de aceitacao**
- Given `SMOKE_LOGIN_EMAIL` e `SMOKE_LOGIN_PASSWORD` configurados, When `./scripts/smoke_vps.sh` roda contra a VPS, Then `GET /auth/me` e `GET /leads?page=1&page_size=10` retornam `200`.
- Given credenciais de smoke ausentes, When o script roda, Then ele continua validando `GET /health`, `GET /docs`, `GET /`, `GET /eventos` e reporta explicitamente que a parte autenticada foi pulada.

## Artifact Minimo do Epico

- `artifacts/phase-f3/epic-f3-01-deploy-backend-vps.md` com evidencias do contrato Compose, do smoke autenticado e do status final do backend na VPS.

## Dependencias

- [PRD](../prd_vps_migration.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
