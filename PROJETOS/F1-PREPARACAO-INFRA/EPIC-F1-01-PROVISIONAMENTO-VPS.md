---
doc_id: "EPIC-F1-01-PROVISIONAMENTO-VPS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F1-01 - Provisionamento VPS

## Objetivo

Entregar um processo idempotente e auditavel para preparar uma VPS Hostinger Ubuntu 22.04 com usuario `deploy`, Docker, Docker Compose, hardening basico e contrato minimo de ambiente para a stack atual do NPBB.

## Resultado de Negocio Mensuravel

Uma VPS nova pode ser preparada de forma repetivel e com baixo drift operacional, reduzindo tempo manual de setup e risco de erro humano antes do primeiro deploy da stack.

## Definition of Done

- Existe um bootstrap idempotente em `Infra/production/scripts/init-vps.sh`.
- `docs/DEPLOY_HOSTINGER_VPS.md` passa a tratar o script acima como caminho oficial de bootstrap.
- `Infra/production/.env.example` cobre todas as variaveis exigidas por `scripts/deploy_vps.sh` e `scripts/smoke_vps.sh` no modo IP.
- O baseline do host inclui `deploy`, grupo `docker`, diretorios `/opt/npbb/app`, `/opt/npbb/env`, `/opt/npbb/backups/postgres`, `/opt/npbb/certs`, `ufw` com `22/80/443` e `fail2ban` ativo.
- O epico gera `artifacts/phase-f1/epic-f1-01-provisionamento-vps.md`.

## Issues

### ISSUE-F1-01-01 - Automatizar bootstrap idempotente da VPS
Status: todo

**User story**
Como pessoa responsavel pela infraestrutura, quero um bootstrap idempotente da VPS para preparar hosts novos sem drift manual.

**Plano TDD**
1. `Red`: ampliar o contrato operacional em `docs/DEPLOY_HOSTINGER_VPS.md` e adicionar verificacao em `scripts/check_repo_hygiene.sh` ou em `scripts/check_production_stack_contracts.sh` para falhar quando faltarem pacotes, diretorios base ou o usuario `deploy` no fluxo documentado.
2. `Green`: criar `Infra/production/scripts/init-vps.sh` para instalar `ca-certificates`, `curl`, `git`, `ufw`, `fail2ban`, Docker Engine e Docker Compose plugin, criar o usuario `deploy`, adiciona-lo ao grupo `docker` e provisionar diretorios em `/opt/npbb`.
3. `Refactor`: centralizar no script os defaults `DEPLOY_USER=deploy`, `APP_ROOT=/opt/npbb` e `SSH_PORT=22`, mantendo `docs/DEPLOY_HOSTINGER_VPS.md` derivado desse contrato.

**Criterios de aceitacao**
- Given uma VPS Ubuntu 22.04 limpa, When `sudo bash Infra/production/scripts/init-vps.sh` roda duas vezes, Then os pacotes, usuario, grupo e diretorios esperados existem sem erro fatal por reexecucao.
- Given drift entre script e documentacao, When o check de contratos da stack roda, Then a validacao falha ate que `docs/DEPLOY_HOSTINGER_VPS.md` reflita o bootstrap real.

### ISSUE-F1-01-02 - Formalizar contrato de ambiente e preflight de deploy
Status: todo

**User story**
Como pessoa que vai subir a stack, quero um `.env` canonico e um preflight de deploy para detectar configuracao faltante antes de build e subida de containers.

**Plano TDD**
1. `Red`: endurecer `scripts/deploy_vps.sh` para falhar quando uma variavel usada por deploy ou smoke nao estiver declarada em `Infra/production/.env.example`.
2. `Green`: revisar `Infra/production/.env.example` para cobrir integralmente o modo IP da F1, separando com clareza variaveis obrigatorias agora e variaveis de dominio/TLS que ficam fora do gate da fase.
3. `Refactor`: adicionar modo `--check-only` em `scripts/deploy_vps.sh` para validar env, diretorios e `docker compose config` sem buildar a stack.

**Criterios de aceitacao**
- Given uma copia de `Infra/production/.env.example` para `/opt/npbb/env/.env.production`, When `./scripts/deploy_vps.sh --check-only /opt/npbb/env/.env.production` roda, Then o preflight passa em modo IP sem exigir dominios ou certificados.
- Given uma variavel obrigatoria ausente para o modo IP, When o preflight roda, Then ele falha com mensagem explicita apontando a chave faltante.

### ISSUE-F1-01-03 - Endurecer baseline operacional do host
Status: todo

**User story**
Como pessoa responsavel pela operacao, quero uma baseline minima de seguranca e acesso para nao subir a stack em um host fragil ou com acesso inseguro.

**Plano TDD**
1. `Red`: fazer o contrato de bootstrap falhar quando nao houver `ufw`, `fail2ban`, instrucao de chave SSH e proibicao do fluxo root como caminho normal de operacao.
2. `Green`: incorporar no `init-vps.sh` a configuracao de `ufw` para `22/80/443`, habilitacao de `fail2ban` e instrucoes objetivas de `authorized_keys` e endurecimento pos-bootstrap em `docs/DEPLOY_HOSTINGER_VPS.md`.
3. `Refactor`: manter portas, usuario e caminhos parametrizados no script, sem multiplicar comandos duplicados na documentacao.

**Criterios de aceitacao**
- Given a VPS bootstrapada, When `ufw status`, `systemctl status fail2ban` e `groups deploy` sao inspecionados, Then o host atende ao baseline operacional da fase.
- Given a documentacao oficial de bootstrap, When uma pessoa operadora a segue do zero, Then o fluxo conduz para uso de `deploy` com chave SSH como caminho padrao de operacao.

## Artifact Minimo do Epico

- `artifacts/phase-f1/epic-f1-01-provisionamento-vps.md`

## Dependencias

- [PRD](../MIGRACAO-VPS-HOSTINGER/prd_vps_migration.md)
- [SCRUM-GOV](../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../COMUM/DECISION-PROTOCOL.md)
