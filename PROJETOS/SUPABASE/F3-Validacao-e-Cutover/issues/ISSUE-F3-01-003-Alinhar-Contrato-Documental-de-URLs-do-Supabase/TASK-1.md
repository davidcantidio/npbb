---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-01-003-Alinhar-Contrato-Documental-de-URLs-do-Supabase"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# T1 - Corrigir exemplos e instrucoes do troubleshooting

## objetivo

Alinhar `docs/TROUBLESHOOTING.md` com o contrato atual de runtime e operacoes
sensiveis do Supabase.

## precondicoes

- revisao pos-issue de `ISSUE-F3-01-001` aprovada com destino `issue-local`
- contrato de referencia confirmado em `backend/.env.example` e `backend/app/db/database.py`

## arquivos_a_ler_ou_tocar

- `docs/TROUBLESHOOTING.md`
- `backend/.env.example`
- `backend/app/db/database.py`

## passos_atomicos

1. revisar os trechos de `docs/TROUBLESHOOTING.md` que exemplificam `DATABASE_URL` e `DIRECT_URL`
2. corrigir exemplos que induzam uso indiferenciado de conexao direta no runtime
3. manter explicita a separacao: `DATABASE_URL` para API; `DIRECT_URL` para migrations/seed
4. revisar a secao de validacao com Supabase para garantir que ela nao contradiz o contrato acima

## comandos_permitidos

- `rg -n "DATABASE_URL|DIRECT_URL|5432|6543|pooler|conexao direta" docs/TROUBLESHOOTING.md backend/.env.example backend/app/db/database.py`

## resultado_esperado

`docs/TROUBLESHOOTING.md` passa a refletir o contrato documental vigente sem
exemplos contraditorios.

## testes_ou_validacoes_obrigatorias

- confirmar que nao resta exemplo em `docs/TROUBLESHOOTING.md` sugerindo `DATABASE_URL` em `:5432` como padrao de runtime
- confirmar que o texto preserva `DIRECT_URL` para migrations/seed

## stop_conditions

- parar se o contrato de referencia em `backend/.env.example` tiver mudado e exigir nova decisao de fase
