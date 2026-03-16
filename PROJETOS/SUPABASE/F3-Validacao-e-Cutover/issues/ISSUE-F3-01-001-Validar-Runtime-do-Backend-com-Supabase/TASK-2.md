---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase"
task_id: "T2"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T2 - Iniciar API e executar checks de disponibilidade

## objetivo

Validar o boot da API e os checks basicos de disponibilidade com o Supabase como banco de runtime.

## precondicoes

- T1 concluida; ambiente apontando para o Supabase

## arquivos_a_ler_ou_tocar

- `scripts/dev_backend.sh`
- `backend/app/db/database.py`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`

## passos_atomicos

1. iniciar a API com o launcher oficial da raiz do repo ou comando equivalente suportado
2. validar pelo menos os checks basicos de disponibilidade do backend em execucao
3. confirmar que a aplicacao nao caiu em fallback SQLite ou dependencia de PostgreSQL local
4. registrar qualquer erro objetivo de conexao, timeout ou incompatibilidade de runtime

## comandos_permitidos

- `source backend/.venv/bin/activate && ./scripts/dev_backend.sh`
- `curl -sf http://127.0.0.1:8000/health`

## resultado_esperado

Backend iniciado e respondendo com o Supabase como banco de runtime.

## testes_ou_validacoes_obrigatorias

- `curl -sf http://127.0.0.1:8000/health`

## stop_conditions

- parar se a API nao subir, se usar banco incorreto ou se os checks minimos falharem
