---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-01-003-Alinhar-Contrato-Documental-de-URLs-do-Supabase"
task_id: "T2"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# T2 - Corrigir a consolidacao de deploy e runtime

## objetivo

Corrigir a consolidacao documental de F3 em `docs/DEPLOY_RENDER_CLOUDFLARE.md`
para remover a ambiguidade entre runtime da API e conexao direta de banco.

## precondicoes

- T1 concluida
- contrato documental de URLs ja estabilizado em `docs/TROUBLESHOOTING.md`

## arquivos_a_ler_ou_tocar

- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `backend/.env.example`
- `scripts/dev_backend.sh`

## passos_atomicos

1. revisar a secao `Estado operacional validado (F3)` e as variaveis obrigatorias de deploy
2. substituir a formulacao que trata `DATABASE_URL` como "conexao direta ou pooler" por texto coerente com o contrato da fase
3. preservar a evidencia de boot e de checks minimos sem reintroduzir equivalencia indevida entre runtime e `DIRECT_URL`
4. garantir que o runbook continue apontando o launcher oficial `./scripts/dev_backend.sh` como referencia de validacao local

## comandos_permitidos

- `rg -n "DATABASE_URL|DIRECT_URL|pooler|conexao direta|health|landing" docs/DEPLOY_RENDER_CLOUDFLARE.md backend/.env.example scripts/dev_backend.sh`

## resultado_esperado

`docs/DEPLOY_RENDER_CLOUDFLARE.md` descreve o estado operacional validado sem
drift sobre o papel de `DATABASE_URL` e `DIRECT_URL`.

## testes_ou_validacoes_obrigatorias

- confirmar que nao resta a frase "conexao direta ou pooler" associada ao runtime em `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- confirmar que a secao continua sustentando os checks `GET /health` e `GET /eventos/{id}/landing`

## stop_conditions

- parar se a correcao exigir redefinir a politica de deploy do projeto alem do escopo documental local
