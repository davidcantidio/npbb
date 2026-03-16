---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-007-Sincronizar-Cascata-Documental-do-Fechamento-da-F1"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
---

# T1 - Corrigir manifesto do epico

## objetivo

Remover a duplicidade da `ISSUE-F1-01-006` no epico e recalcular o status do
`EPIC-F1-01`.

## precondicoes

`ISSUE-F1-01-006` lida; regras de cascata em `GOV-SCRUM.md` compreendidas;
sem necessidade de alterar a issue de origem.

## arquivos_a_ler_ou_tocar

- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`

## passos_atomicos

1. localizar as duas linhas da `ISSUE-F1-01-006` na tabela `Issues do Epico`
2. remover apenas a linha residual com status `todo`
3. manter a linha final da issue com status `done`
4. recalcular o status do epico para `done`, ja que todas as issues filhas
   ficam encerradas
5. nao alterar objetivo, DoD do epico ou qualquer outra issue da tabela

## comandos_permitidos

- `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- `rg -n "ISSUE-F1-01-006|status:" PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`

## resultado_esperado

Epico sem duplicidade da issue e com status `done`.

## testes_ou_validacoes_obrigatorias

- confirmar por leitura que a tabela contem uma unica linha da `ISSUE-F1-01-006`
- confirmar por leitura que o frontmatter do epico ficou `status: "done"`

## stop_conditions

- parar se a correcao exigir reabrir a issue original, alterar sprint ou
  mexer em artefato fora do epico
