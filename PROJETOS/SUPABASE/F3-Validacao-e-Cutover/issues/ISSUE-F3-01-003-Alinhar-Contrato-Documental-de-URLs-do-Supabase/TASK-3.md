---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F3-01-003-Alinhar-Contrato-Documental-de-URLs-do-Supabase"
task_id: "T3"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# T3 - Validar coerencia final do contrato documental

## objetivo

Fechar a issue somente quando troubleshooting, deploy e contrato base de
configuracao estiverem coerentes entre si.

## precondicoes

- T1 e T2 concluidas

## arquivos_a_ler_ou_tocar

- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `backend/.env.example`
- `backend/app/db/database.py`

## passos_atomicos

1. revisar os textos finais dos documentos alterados contra `backend/.env.example`
2. confirmar que `backend/app/db/database.py` continua compativel com a narrativa documental consolidada
3. executar uma varredura textual para garantir que nao restaram instrucoes contraditorias sobre `DATABASE_URL` e `DIRECT_URL`
4. consolidar a issue somente se o contrato documental final estiver unificado

## comandos_permitidos

- `rg -n "DATABASE_URL|DIRECT_URL|5432|6543|pooler|conexao direta" docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md backend/.env.example backend/app/db/database.py`

## resultado_esperado

Os documentos operacionais da F3 passam a compartilhar o mesmo contrato de URLs
do Supabase, sem drift residual.

## testes_ou_validacoes_obrigatorias

- confirmar coerencia entre `backend/.env.example`, `docs/TROUBLESHOOTING.md` e `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- confirmar que a issue de origem segue sem necessidade de reabertura

## stop_conditions

- parar se restar ambiguidade documental que dependa de novo intake ou de redefinicao estrutural da fase
