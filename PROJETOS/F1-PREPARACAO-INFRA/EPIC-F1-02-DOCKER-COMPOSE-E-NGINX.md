---
doc_id: "EPIC-F1-02-DOCKER-COMPOSE-E-NGINX"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F1-02 - Docker Compose e Nginx

## Objetivo

Fechar o contrato operacional da stack de producao existente, mantendo os servicos `postgres`, `api`, `web`, `edge` e `backup`, consolidando o modo IP do Nginx e fortalecendo os smokes que comprovam o gate da F1.

## Resultado de Negocio Mensuravel

A stack Hostinger deixa de ser um scaffold parcial e passa a ter um caminho operacional verificavel para subir, responder em HTTP e evidenciar prontidao antes da fase de migracao de dados.

## Definition of Done

- `Infra/production/docker-compose.yml` representa explicitamente a stack canonica da F1 com healthchecks e dependencias coerentes.
- O servico `edge` fica explicitado como o Nginx da stack, com `render.sh` e templates consistentes para o modo IP.
- `scripts/deploy_vps.sh` e `scripts/smoke_vps.sh` comprovam o gate da fase sem depender de dominio ou TLS.
- O servico `backup` participa do contrato operacional minimo da stack, ainda que a prova completa de restore fique para fase posterior.
- O epico gera `artifacts/phase-f1/epic-f1-02-docker-compose-e-nginx.md`.

## Issues

### ISSUE-F1-02-01 - Auditar contrato do docker-compose e healthchecks
Status: todo

**User story**
Como pessoa mantenedora da stack, quero um contrato explicito do `docker-compose` para garantir que a VPS sobe sempre os mesmos servicos com dependencias e healthchecks verificaveis.

**Plano TDD**
1. `Red`: endurecer `scripts/deploy_vps.sh --check-only` e a validacao de compose para falhar quando a stack nao expuser exatamente `postgres`, `api`, `web`, `edge` e `backup`, ou quando faltar `restart: unless-stopped` e healthchecks minimos.
2. `Green`: revisar `Infra/production/docker-compose.yml` para manter os cinco servicos atuais, com healthchecks em `postgres`, `api`, `web`, `edge` e um contrato operacional verificavel para `backup`.
3. `Refactor`: extrair para funcoes shell reutilizaveis a validacao de servicos, healthchecks e diretorios exigidos, reduzindo duplicacao em `scripts/deploy_vps.sh`.

**Criterios de aceitacao**
- Given um env valido de producao em modo IP, When `./scripts/deploy_vps.sh --check-only /opt/npbb/env/.env.production` roda, Then `docker compose config` valida a stack canonica da F1 sem drift de nomes de servico.
- Given a stack subida na VPS, When `docker compose ps` e inspecionado, Then `postgres`, `api`, `web`, `edge` e `backup` aparecem saudaveis/operacionais conforme o contrato definido para a fase.

### ISSUE-F1-02-02 - Consolidar renderizacao Nginx em modo IP
Status: todo

**User story**
Como pessoa responsavel pelo trafego inicial, quero que o Nginx da VPS funcione em modo IP na F1 para validar backend e frontend antes de qualquer decisao de dominio ou TLS.

**Plano TDD**
1. `Red`: ampliar `scripts/smoke_vps.sh`, `Infra/production/nginx/render.sh` e `Infra/production/nginx/conf.d/ip.conf.template` para falhar quando `/api/health`, `/api/docs`, `/` ou `/eventos` nao forem atendidos corretamente no modo IP.
2. `Green`: consolidar `DEPLOY_MODE=ip` como padrao do gate da fase, mantendo `ip.conf.template` como template obrigatorio da F1 e deixando templates de dominio/TLS isolados para fases posteriores.
3. `Refactor`: documentar no epico e em `docs/DEPLOY_HOSTINGER_VPS.md` a equivalencia conceitual `edge = nginx`, evitando ambiguidade entre PRD e scaffold atual.

**Criterios de aceitacao**
- Given `DEPLOY_MODE=ip`, When `edge` sobe com o env da fase, Then `http://<PUBLIC_HOST>/api/health`, `http://<PUBLIC_HOST>/api/docs`, `http://<PUBLIC_HOST>/` e `http://<PUBLIC_HOST>/eventos` respondem conforme o smoke esperado.
- Given a F1 ainda nao cobre dominio ou TLS, When o gate da fase roda, Then nenhuma variavel de dominio ou certificado e exigida para aprovacao.

### ISSUE-F1-02-03 - Fortalecer smoke operacional e evidencia da fase
Status: todo

**User story**
Como pessoa que aprova a fase, quero um smoke operacional objetivo para decidir se a stack IP esta pronta para avancar a migracao do banco.

**Plano TDD**
1. `Red`: endurecer `scripts/smoke_vps.sh` para falhar quando houver container nao saudavel, `/api/docs` sem `Swagger UI`, SPA sem `id="root"` ou `/auth/login` com comportamento inesperado para credenciais invalidas.
2. `Green`: fazer `scripts/smoke_vps.sh` verificar container health, endpoints HTTP obrigatorios, smoke de login invalido e, opcionalmente, smoke autenticado quando `SMOKE_LOGIN_*` estiver preenchido.
3. `Refactor`: organizar o script em helpers reutilizaveis e padronizar a evidencia consolidada em `artifacts/phase-f1/epic-f1-02-docker-compose-e-nginx.md`.

**Criterios de aceitacao**
- Given a stack IP recem-subida na VPS, When `./scripts/smoke_vps.sh /opt/npbb/env/.env.production` roda, Then o script valida `/api/health`, `/api/docs`, `/`, `/eventos` e o comportamento esperado de `/auth/login`.
- Given qualquer endpoint obrigatorio ou servico de stack fora do contrato, When o smoke roda, Then ele encerra com status nao-zero e identifica claramente a falha.

## Artifact Minimo do Epico

- `artifacts/phase-f1/epic-f1-02-docker-compose-e-nginx.md`

## Dependencias

- [PRD](../MIGRACAO-VPS-HOSTINGER/prd_vps_migration.md)
- [SCRUM-GOV](../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../COMUM/DECISION-PROTOCOL.md)
