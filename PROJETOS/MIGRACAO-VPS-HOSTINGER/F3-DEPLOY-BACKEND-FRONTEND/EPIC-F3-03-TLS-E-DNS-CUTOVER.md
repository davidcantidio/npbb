---
doc_id: "EPIC-F3-03-TLS-E-DNS-CUTOVER"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F3-03 - TLS e DNS Cutover

## Objetivo

Executar o cutover final para HTTPS em dominio usando Cloudflare DNS-only e Let's Encrypt no VPS, com medicao de latencia, validacao de certificado e rollback operacional claro.

## Resultado de Negocio Mensuravel

O trafego real passa a chegar no ambiente Hostinger por HTTPS com latencia previsivel e rollback curto, sem dependencias de proxy Cloudflare ou de provedores legados de deploy.

## Definition of Done

- O runbook de deploy e cutover passa a refletir DNS-only e Let's Encrypt como modelo canonico.
- O contrato de env inclui `CERTBOT_EMAIL` e os caminhos finais de certificado usados pelo `edge`.
- O smoke da fase mede latencia de `auth/me` e `leads` e falha acima de `500ms`.
- Existe rollback documentado para as primeiras 24h pos-cutover, sem desligar Render ou Supabase nesta fase.

## Issues

### ISSUE-F3-03-01 - Alinhar docs e env ao modelo canonico DNS-only e Let's Encrypt
Status: todo

**User story**
Como pessoa responsavel pela arquitetura de producao, quero que o runbook e o env reflitam o modelo canonico do PRD para evitar um cutover executado com premissas contraditorias.

**Plano TDD**
1. `Red`: criar `tests/test_vps_docs_contract.py` para falhar se `docs/DEPLOY_HOSTINGER_VPS.md`, `Infra/production/.env.example` e `scripts/deploy_vps.sh` continuarem tratando Cloudflare `proxied` e `origin.crt` ou `origin.key` como caminho canonico de producao.
2. `Green`: reescrever `docs/DEPLOY_HOSTINGER_VPS.md`, `Infra/production/.env.example` e `scripts/deploy_vps.sh` para DNS-only, adicionar `CERTBOT_EMAIL`, fixar o uso de `/etc/nginx/certs/fullchain.pem` e `/etc/nginx/certs/privkey.pem` dentro do `edge`, e documentar a emissao via Certbot no host.
3. `Refactor`: eliminar referencias legadas a origin cert como padrao do projeto e manter um unico caminho oficial de configuracao TLS.

**Criterios de aceitacao**
- Given a documentacao operacional da F3, When lida por uma pessoa de infraestrutura, Then o modelo canonico descrito e Cloudflare DNS-only com TLS emitido no VPS.
- Given `ENABLE_TLS=true`, When o contrato de env e avaliado, Then `APP_DOMAIN`, `API_DOMAIN`, `CERTBOT_EMAIL`, `TLS_CERT_PATH` e `TLS_KEY_PATH` estao definidos e coerentes com o `edge`.

### ISSUE-F3-03-02 - Medir HTTPS e latencia dos endpoints criticos apos o cutover
Status: todo

**User story**
Como pessoa que aprova a virada para dominio, quero uma medicao objetiva de HTTPS e tempo de resposta para decidir a promocao da F3 com base em evidencia.

**Plano TDD**
1. `Red`: criar `tests/test_vps_latency_contract.py` e ampliar `scripts/smoke_vps.sh` para falhar quando o script nao medir `curl -w '%{time_total}'` em `GET /auth/me` e `GET /leads?page=1&page_size=10`.
2. `Green`: atualizar `scripts/smoke_vps.sh` para emitir latencia, validar certificado HTTPS e bloquear quando qualquer endpoint critico exceder `0.500s`.
3. `Refactor`: extrair helpers de `http_code` e `time_total` em `scripts/smoke_vps.sh` para reduzir duplicacao entre checks publicos e autenticados.

**Criterios de aceitacao**
- Given `DEPLOY_MODE=domain`, `ENABLE_TLS=true` e credenciais de smoke validas, When `./scripts/smoke_vps.sh` roda, Then `health`, `auth/me` e `leads?page=1&page_size=10` retornam `200`, e `auth/me` e `leads` ficam abaixo de `500ms`.
- Given certificado invalido, DNS errado ou TLS nao emitido, When o smoke roda, Then a falha e explicita e a F3 nao pode ser dada como concluida.

### ISSUE-F3-03-03 - Formalizar rollback e observabilidade das primeiras 24h
Status: todo

**User story**
Como pessoa que conduz o cutover, quero um rollback curto e um periodo de observacao claro para reagir rapidamente a incidentes sem perder o estado do novo ambiente.

**Plano TDD**
1. `Red`: ampliar `tests/test_vps_docs_contract.py` para falhar se `docs/DEPLOY_HOSTINGER_VPS.md` e `docs/RUNBOOK_RESTORE_POSTGRES_VPS.md` nao cobrirem TTL, reversao do registro A, comandos de `docker compose ps` e `docker compose logs edge api`, e a regra de manter Render e Supabase ativos por pelo menos 24h.
2. `Green`: atualizar `docs/DEPLOY_HOSTINGER_VPS.md` e `docs/RUNBOOK_RESTORE_POSTGRES_VPS.md` com a sequencia de pre-cutover, cutover, observacao e rollback.
3. `Refactor`: manter apenas um caminho oficial de cutover e um caminho oficial de restore e rollback, sem instrucoes concorrentes.

**Criterios de aceitacao**
- Given uma janela de observacao pos-cutover, When o runbook e seguido, Then existem comandos explicitos para `docker compose ps`, `docker compose logs edge api` e reversao do DNS.
- Given incidente nas primeiras 24h, When o rollback e executado, Then o trafego pode voltar para a stack anterior sem destruir o ambiente da VPS nem encerrar servicos legados prematuramente.

## Artifact Minimo do Epico

- `artifacts/phase-f3/epic-f3-03-tls-e-dns-cutover.md` com evidencias do modelo TLS canonico, das medicoes de latencia e do rollback documentado.

## Dependencias

- [PRD](../prd_vps_migration.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
