---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T1 - Mapear pontos de drift documental e de configuracao

## objetivo

Localizar todas as inconsistencias documentais e de configuracao que ainda tratam o PostgreSQL local como caminho principal.

## precondicoes

- EPIC-F3-01 concluido ou sem bloqueios objetivos

## arquivos_a_ler_ou_tocar

- `backend/.env.example`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `docs/render.yaml`

## passos_atomicos

1. revisar cada arquivo alvo procurando instrucoes que ainda coloquem PostgreSQL local como requisito padrao
2. marcar quais trechos devem ser atualizados para refletir Supabase como banco unico
3. preservar as excecoes legitimas de testes com SQLite e qualquer observacao que continue relevante para o backend
4. consolidar o inventario de drift antes de editar os documentos

## comandos_permitidos

- `rg -n "postgresql@16|createdb npbb|DATABASE_URL|DIRECT_URL|Supabase|SQLite|TESTING" backend/.env.example docs/SETUP.md docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md docs/render.yaml`

## resultado_esperado

Inventario fechado das inconsistencias documentais e de configuracao.

## testes_ou_validacoes_obrigatorias

- confirmar que o inventario cobre setup, troubleshooting, deploy e exemplo de env

## stop_conditions

- parar se surgir dependencia operacional nova nao validada em F3
