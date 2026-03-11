---
doc_id: "EPIC-F4-02-BACKUP-AUTOMATIZADO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F4-02 - Backup Automatizado

## Objetivo

Garantir backup diario do Postgres com retencao operacional, copia para volume externo e restore drill comprovando recuperacao completa em ate 30 minutos.

## Resultado de Negocio Mensuravel

A continuidade do sistema deixa de depender do banco anterior e passa a contar com recuperacao auditavel diretamente na VPS Hostinger.

## Definition of Done

- o container `backup` gera dump diario em formato custom e loga inicio, sucesso ou falha
- a retencao mantem 7 dumps diarios e 4 dumps semanais
- cada dump e copiado para volume externo montado em `/opt/npbb/backups/archive`
- cada execucao gera checksum do dump
- existe restore drill automatizado usando o dump mais recente e smoke posterior

## Issues

### ISSUE-F4-02-01 - Endurecer politica de dump e retencao
Status: todo

**User story**
Como responsavel por operacao, quero endurecer a politica de dump e retencao para que o backup nao cresca sem controle e continue rastreavel.

**Plano TDD**
1. `Red`: em `Infra/production/backup/backup.sh`, `Infra/production/backup/crontab`, `Infra/production/backup/start-crond.sh` e novo `tests/test_vps_backup_policy.py` para falhar sem retencao 7+4 e logs estruturados.
2. `Green`: implementar rotacao diaria e semanal, logs com nome do arquivo e checksum e status final visivel em `docker logs backup`.
3. `Refactor`: extrair helpers de retencao e padronizar nomes de arquivo.

**Criterios de aceitacao**
- Given multiplos dumps historicos, When a rotacao executa, Then permanecem apenas os 7 diarios mais recentes e os 4 semanais mais recentes.
- Given execucao do cron, When o operador consulta `docker logs backup`, Then ve inicio, sucesso ou falha e o arquivo gerado.

### ISSUE-F4-02-02 - Copiar dump e checksum para volume externo
Status: todo

**User story**
Como pessoa dona da recuperacao, quero copiar o dump para um volume externo montado no host para reduzir risco de perda local.

**Plano TDD**
1. `Red`: em `Infra/production/docker-compose.yml`, `Infra/production/.env.example`, `docs/DEPLOY_HOSTINGER_VPS.md` e `tests/test_vps_backup_policy.py` para falhar sem diretorio externo e manifesto de integridade.
2. `Green`: adicionar `BACKUP_EXTERNAL_HOST_DIR=/opt/npbb/backups/archive`, gerar `.sha256` e copiar dump e checksum para o volume externo.
3. `Refactor`: consolidar o contrato de env entre compose, script e documentacao.

**Criterios de aceitacao**
- Given backup local bem-sucedido, When a execucao termina, Then o dump e seu checksum existem no volume externo.
- Given indisponibilidade do volume externo, When o backup roda, Then a execucao falha explicitamente e nao reporta sucesso.

### ISSUE-F4-02-03 - Validar restore drill periodico
Status: todo

**User story**
Como pessoa que aprova a migracao, quero validar um restore drill periodico para que o tempo de recuperacao maximo seja comprovado.

**Plano TDD**
1. `Red`: em `docs/RUNBOOK_RESTORE_POSTGRES_VPS.md`, `scripts/smoke_vps.sh` e novo `scripts/restore_backup_drill.sh` para falhar sem drill automatizado.
2. `Green`: criar restore do dump mais recente em ambiente descartavel, seguido de smoke e medicao de duracao total.
3. `Refactor`: reutilizar carga de env e comandos de compose ja existentes.

**Criterios de aceitacao**
- Given o dump arquivado mais recente, When o restore drill e executado, Then o sistema volta a smoke-green em ate 30 minutos.
- Given dump corrompido ou ausente, When o drill roda, Then o erro fica explicito e bloqueia a promocao da fase.

## Artifact Minimo do Epico

- `artifacts/phase-f4/epic-f4-02-backup-automatizado.md`

## Dependencias

- [PRD](../prd_vps_migration.md)
- [GOV-SCRUM](../../../../COMUM/GOV-SCRUM.md)
- [GOV-DECISOES](../../../../COMUM/GOV-DECISOES.md)
