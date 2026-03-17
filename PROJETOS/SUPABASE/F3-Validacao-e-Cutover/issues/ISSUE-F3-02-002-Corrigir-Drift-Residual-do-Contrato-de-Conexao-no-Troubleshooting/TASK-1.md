---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-02-002-Corrigir-Drift-Residual-do-Contrato-de-Conexao-no-Troubleshooting"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T1 - Corrigir o trecho residual de contrato em docs/TROUBLESHOOTING.md

## objetivo

Remover a contradicao residual em `docs/TROUBLESHOOTING.md` sobre o papel de
`DATABASE_URL` e `DIRECT_URL` no estado final da F3.

## precondicoes

- issue de origem revisada e achado confirmado
- contrato documental atual de `backend/.env.example` e `docs/SETUP.md` lido antes de editar

## arquivos_a_ler_ou_tocar

- `docs/TROUBLESHOOTING.md`
- `backend/.env.example`
- `docs/SETUP.md`

## passos_atomicos

1. reler o exemplo inicial de conexao em `docs/TROUBLESHOOTING.md` e marcar exatamente onde ele contradiz o contrato consolidado da F3
2. comparar o trecho com `backend/.env.example` e `docs/SETUP.md` para preservar a mesma semantica de runtime vs conexao direta
3. ajustar apenas o necessario em `docs/TROUBLESHOOTING.md` para deixar explicito que `DATABASE_URL` e usada pela API e `DIRECT_URL` por migrations/seed, sem reabrir outros temas de deploy
4. revisar o item 13 do proprio troubleshooting para garantir que o exemplo corrigido e a orientacao textual contam a mesma historia
5. parar sem fechar a task se surgir contradicao nova fora do escopo local da issue

## comandos_permitidos

- `rg -n "DATABASE_URL|DIRECT_URL|5432|6543|pooler|Supabase" docs/TROUBLESHOOTING.md backend/.env.example docs/SETUP.md`

## resultado_esperado

`docs/TROUBLESHOOTING.md` deixa de induzir o uso indiferenciado de conexao direta
nas duas variaveis e volta a refletir o contrato final documentado da F3.

## testes_ou_validacoes_obrigatorias

- confirmar leitura lado a lado de `docs/TROUBLESHOOTING.md`, `backend/.env.example` e `docs/SETUP.md`
- confirmar que o exemplo corrigido nao contradiz o item de "pooler vs conexao direta" do proprio troubleshooting

## stop_conditions

- parar se `backend/.env.example` ou `docs/SETUP.md` mostrarem contrato diferente do esperado pela issue
- parar se a correcao exigir alterar `docs/DEPLOY_RENDER_CLOUDFLARE.md`, `docs/render.yaml` ou codigo do backend para manter coerencia
