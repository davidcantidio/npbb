# Artifact - EPIC-F4-01 Pipeline Deploy SSH

## Estado Atual

Status do artifact: `pending-execution`.

Este arquivo concentra a evidencia minima de build, sincronizacao do `dist`, deploy remoto por SSH e rollback por commit SHA.

## Pipeline

- Workflow dedicado: implementado, aguardando execucao em `main`.
- Build do frontend: aguardando primeira execucao auditavel.
- Sincronizacao de `frontend/dist`: aguardando evidencia de producao.

## Deploy Remoto

- `scripts/deploy_vps.sh`: implementado, aguardando execucao em VPS.
- `alembic upgrade head`: aguardando evidencia de producao.
- `scripts/smoke_vps.sh`: aguardando evidencia de producao.

## Rollback

- Procedimento por commit SHA: documentado.
- Ultimo SHA implantado: nao executado.
- Resultado do rollback manual: nao executado.

## Observacoes

- Enquanto este artifact estiver em `pending-execution`, a decisao final da fase permanece `hold`.
