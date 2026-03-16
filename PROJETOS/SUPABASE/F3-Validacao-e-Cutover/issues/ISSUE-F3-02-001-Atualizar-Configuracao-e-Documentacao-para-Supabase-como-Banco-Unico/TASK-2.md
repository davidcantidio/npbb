---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T2 - Atualizar configuracao e setup para Supabase como banco unico

## objetivo

Atualizar os artefatos de configuracao e setup para refletir o Supabase como banco unico do projeto.

## precondicoes

- T1 concluida; inventario de drift fechado

## arquivos_a_ler_ou_tocar

- `backend/.env.example`
- `docs/SETUP.md`
- `scripts/dev_backend.sh`

## passos_atomicos

1. alinhar `backend/.env.example` ao papel final de `DATABASE_URL` e `DIRECT_URL`
2. ajustar `docs/SETUP.md` para remover PostgreSQL local como requisito operacional principal e deixar claro o fallback de testes
3. conferir se o launcher oficial em `scripts/dev_backend.sh` continua coerente com o setup resultante
4. manter fora do escopo qualquer alteracao de frontend ou Supabase Auth

## comandos_permitidos

- `rg -n "DATABASE_URL|DIRECT_URL|postgresql@16|createdb npbb" backend/.env.example docs/SETUP.md scripts/dev_backend.sh`

## resultado_esperado

Configuracao e setup alinhados ao Supabase como banco unico.

## testes_ou_validacoes_obrigatorias

- confirmar que o setup final ainda preserva `TESTING=true` como caminho de SQLite para testes

## stop_conditions

- parar se a mudanca documental exigir alterar o contrato validado de runtime do backend
