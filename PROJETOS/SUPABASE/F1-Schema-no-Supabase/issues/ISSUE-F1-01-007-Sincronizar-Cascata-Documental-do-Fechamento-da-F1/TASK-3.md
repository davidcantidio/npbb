---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F1-01-007-Sincronizar-Cascata-Documental-do-Fechamento-da-F1"
task_id: "T3"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
---

# T3 - Validar coerencia documental final

## objetivo

Validar a coerencia documental final da cascata local.

## precondicoes

T1 e T2 concluidas; nenhum arquivo de codigo alterado nesta issue.

## arquivos_a_ler_ou_tocar

- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md`

## passos_atomicos

1. reler os manifestos do epico e da fase apos as edicoes
2. confirmar que a `ISSUE-F1-01-006` segue `done` e nao foi reaberta
3. confirmar que o epico ficou `done`, a fase segue `active` e o gate ficou
   `pending`
4. confirmar que a remediacao permaneceu documental e local

## comandos_permitidos

- `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- `rg -n "ISSUE-F1-01-006|status:|audit_gate:|gate_atual:|EPIC-F1-01" PROJETOS/SUPABASE/F1-Schema-no-Supabase`

## resultado_esperado

Cascata documental local consistente e pronta para a futura auditoria da F1.

## testes_ou_validacoes_obrigatorias

- confirmar por leitura que nao existe mais linha `todo` residual da `ISSUE-F1-01-006`
- confirmar por leitura que o estado final ficou `issue done -> epico done -> fase active + gate pending`

## stop_conditions

- parar se surgir necessidade de alterar codigo, testes backend ou documentos
  fora da cascata local desta fase
