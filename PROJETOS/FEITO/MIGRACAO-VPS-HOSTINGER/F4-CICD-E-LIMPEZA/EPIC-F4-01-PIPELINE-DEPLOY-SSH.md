---
doc_id: "EPIC-F4-01-PIPELINE-DEPLOY-SSH"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F4-01 - Pipeline Deploy SSH

## Objetivo

Automatizar o deploy de producao via GitHub Actions + SSH, publicando o frontend estatico no host, aplicando atualizacoes do backend e rodando smoke pos-deploy sem depender de Render ou Cloudflare Pages.

## Resultado de Negocio Mensuravel

Um push em `main` passa a produzir uma atualizacao auditavel na VPS, com rollback documentado e sem passo manual obrigatorio para publicar frontend ou backend.

## Definition of Done

- existe `.github/workflows/deploy.yml` separado do `ci.yml`
- o workflow dispara apenas apos `CI` verde em `main`
- o `frontend/dist` e buildado no GitHub Actions e sincronizado para `/opt/npbb/app/frontend/dist`
- o deploy remoto roda `docker compose up -d --build backend nginx backup`, `alembic upgrade head` e `scripts/smoke_vps.sh`
- a documentacao operacional lista segredos, paths e rollback por commit SHA

## Issues

### ISSUE-F4-01-01 - Buildar e publicar o dist do frontend no GitHub Actions
Status: todo

**User story**
Como pessoa responsavel por releases, quero buildar e publicar o `dist/` do frontend no GitHub Actions para que a SPA seja servida pelo Nginx da VPS sem Cloudflare Pages.

**Plano TDD**
1. `Red`: em `.github/workflows/ci.yml`, `.github/workflows/deploy.yml` e `frontend/package.json` para falhar sem artefato `dist`.
2. `Green`: criar workflow com upload/download de artefato e sincronizacao para `/opt/npbb/app/frontend/dist`.
3. `Refactor`: remover duplicacao de setup Node entre CI e deploy.

**Criterios de aceitacao**
- Given push em `main` com CI verde, When o deploy roda, Then o `dist/` chega ao host de producao.
- Given PR ou branch nao `main`, When o workflow dispara, Then nenhum deploy e executado.

### ISSUE-F4-01-02 - Executar deploy remoto por SSH com migracao e smoke
Status: todo

**User story**
Como operador da VPS, quero um deploy remoto por SSH que aplique backend, migracao e smoke em uma sequencia unica para que a publicacao seja reprodutivel.

**Plano TDD**
1. `Red`: em `scripts/deploy_vps.sh`, `scripts/smoke_vps.sh` e `docs/DEPLOY_HOSTINGER_VPS.md` para falhar sem sequencia remota `sync -> compose -> alembic -> smoke`.
2. `Green`: implementar SSH remoto com `rsync` do checkout, uso de `/opt/npbb/env/.env.production` e smoke HTTPS.
3. `Refactor`: consolidar paths e variaveis compartilhadas.

**Criterios de aceitacao**
- Given workflow de deploy em `main`, When o job remoto executa, Then backend, nginx e backup sobem com sucesso e o smoke passa.
- Given falha no smoke, When o job termina, Then o workflow falha e registra o SHA implantado para rollback.

### ISSUE-F4-01-03 - Documentar segredos e rollback por commit SHA
Status: todo

**User story**
Como mantenedor do projeto, quero documentacao explicita de segredos e rollback para que um incidente de producao seja reversivel sem inferencia manual.

**Plano TDD**
1. `Red`: em `docs/DEPLOY_HOSTINGER_VPS.md` e `.github/workflows/deploy.yml` para falhar sem contrato de segredos e rollback.
2. `Green`: documentar `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_PORT`, `VPS_DEPLOY_PATH`, rollback por SHA e fallback manual.
3. `Refactor`: alinhar nomes de variaveis entre doc e workflow.

**Criterios de aceitacao**
- Given falha de release, When o runbook e seguido, Then o rollback para o commit anterior e executavel sem adivinhar paths.
- Given novo mantenedor, When le a doc, Then todos os segredos e pre-requisitos estao explicitos.

## Artifact Minimo do Epico

- `artifacts/phase-f4/epic-f4-01-pipeline-deploy-ssh.md`

## Dependencias

- [PRD](../prd_vps_migration.md)
- [GOV-SCRUM](../../../../COMUM/GOV-SCRUM.md)
- [GOV-DECISOES](../../../../COMUM/GOV-DECISOES.md)
