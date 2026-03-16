---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T3 - Alinhar troubleshooting e deploy ao estado final validado

## objetivo

Alinhar troubleshooting e deploy ao estado final do banco unico validado em F3.

## precondicoes

- T2 concluida

## arquivos_a_ler_ou_tocar

- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `docs/render.yaml`
- `backend/.env.example`

## passos_atomicos

1. ajustar `docs/TROUBLESHOOTING.md` para refletir o novo caminho principal de banco e os gotchas realmente restantes
2. revisar `docs/DEPLOY_RENDER_CLOUDFLARE.md` e `docs/render.yaml` para garantir coerencia com o contrato final de `DATABASE_URL` e `DIRECT_URL`
3. confirmar que deploy e troubleshooting nao reintroduzem PostgreSQL local como dependencia principal
4. preservar as instrucoes de go-live ja existentes que continuam validas

## comandos_permitidos

- `rg -n "DATABASE_URL|DIRECT_URL|Postgres|Supabase|Render" docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md docs/render.yaml backend/.env.example`

## resultado_esperado

Troubleshooting e deploy coerentes com o Supabase como banco unico.

## testes_ou_validacoes_obrigatorias

- confirmar que deploy, setup e troubleshooting descrevem o mesmo contrato de banco

## stop_conditions

- parar se houver contradicao entre o estado final validado e o que a documentacao de deploy permite publicar
