---
doc_id: "TASK-4.md"
issue_id: "ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T4 - Revisao final de consistencia entre arquivos atualizados

## objetivo

Executar a revisao final de consistencia entre todos os arquivos atualizados.

## precondicoes

- T3 concluida

## arquivos_a_ler_ou_tocar

- `backend/.env.example`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `docs/render.yaml`

## passos_atomicos

1. comparar os cinco arquivos lado a lado quanto ao papel de `DATABASE_URL`, `DIRECT_URL`, Supabase e SQLite em testes
2. remover contradicoes residuais ou repeticoes que desviem do estado final validado
3. confirmar que o PostgreSQL local nao aparece mais como requisito operacional padrao
4. liberar a issue somente com um estado documental coerente entre setup, troubleshooting e deploy

## comandos_permitidos

- `rg -n "postgresql@16|createdb npbb|DATABASE_URL|DIRECT_URL|SQLite|Supabase" backend/.env.example docs/SETUP.md docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md docs/render.yaml`

## resultado_esperado

Conjunto documental final coerente com o Supabase como banco unico.

## testes_ou_validacoes_obrigatorias

- confirmar que nao restou instrucao principal para operar o backend com PostgreSQL local

## stop_conditions

- parar se ainda houver contradicao material entre setup, troubleshooting e deploy
