---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-01-007-Sincronizar-Cascata-Documental-do-Fechamento-da-F1"
task_id: "T2"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
---

# T2 - Sincronizar manifesto da fase F1

## objetivo

Alinhar o manifesto da fase F1 ao estado final correto do epico e do gate de
auditoria.

## precondicoes

T1 concluida; estado final do epico confirmado como `done`; entendimento das
regras de gate em `GOV-SCRUM.md` e `GOV-ISSUE-FIRST.md`.

## arquivos_a_ler_ou_tocar

- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`

## passos_atomicos

1. atualizar a linha do `EPIC-F1-01` na tabela de epicos para `done`
2. alinhar o `audit_gate` do frontmatter para `pending`
3. alinhar a secao `Estado do Gate de Auditoria` para o mesmo estado `pending`
4. revisar a checklist local `not_ready -> pending` para que ela nao
   contradiga o estado final do gate
5. nao criar relatorio de auditoria, nao atualizar `AUDIT-LOG` e nao simular
   veredito formal

## comandos_permitidos

- `sed -n '1,120p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- `rg -n "audit_gate:|gate_atual:|EPIC-F1-01|not_ready -> pending" PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`

## resultado_esperado

Manifesto da fase coerente com a F1 pronta para auditoria.

## testes_ou_validacoes_obrigatorias

- confirmar por leitura que `audit_gate` e `gate_atual` ficaram ambos `pending`
- confirmar por leitura que a tabela de epicos mostra `EPIC-F1-01` como `done`

## stop_conditions

- parar se a correcao exigir abrir auditoria formal, alterar `AUDIT-LOG` ou
  tratar a fase como `approved`
