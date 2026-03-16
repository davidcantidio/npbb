---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T1 - Preparar ambiente e conferir contrato de URLs

## objetivo

Garantir que o backend sera validado contra o Supabase e nao contra um banco local residual.

## precondicoes

- F2 concluida; credenciais validas de `DATABASE_URL` e `DIRECT_URL`

## arquivos_a_ler_ou_tocar

- `backend/app/db/database.py`
- `backend/.env.example`
- `scripts/dev_backend.sh`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`

## passos_atomicos

1. revisar em `backend/app/db/database.py` a ordem de resolucao de `DATABASE_URL` e o fallback de testes
2. revisar em `scripts/dev_backend.sh` como o backend e iniciado a partir da raiz do repo
3. conferir se o ambiente de validacao esta apontando para o Supabase e nao para PostgreSQL local
4. bloquear a rodada se houver qualquer indicio de que o runtime ainda usara o banco local

## comandos_permitidos

- `rg -n "DATABASE_URL|TESTING|sqlite" backend/app/db/database.py backend/.env.example scripts/dev_backend.sh docs/DEPLOY_RENDER_CLOUDFLARE.md`

## resultado_esperado

Ambiente de runtime preparado para validar a API diretamente contra o Supabase.

## testes_ou_validacoes_obrigatorias

- confirmar que `DATABASE_URL` do ambiente aponta para o Supabase antes do boot

## stop_conditions

- parar se o ambiente ainda estiver configurado para um PostgreSQL local
