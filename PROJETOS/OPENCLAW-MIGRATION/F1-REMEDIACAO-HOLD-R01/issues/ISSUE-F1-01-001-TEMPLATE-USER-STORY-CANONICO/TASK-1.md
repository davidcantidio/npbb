---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T1 - Criar TEMPLATE-USER-STORY.md

## objetivo

Criar `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` com frontmatter e corpo alinhados a US 2.2 do spec e a `GOV-USER-STORY.md`.

## precondicoes

- Leitura de `GOV-USER-STORY.md` e Task 2.2.1 em `openclaw-migration-spec.md`
- Relatorio R01 B1 como referencia de aceitacao

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/GOV-USER-STORY.md`
- `PROJETOS/OPENCLAW-MIGRATION/openclaw-migration-spec.md`
- `PROJETOS/COMUM/TEMPLATE-TASK.md`
- `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` (criar)

## passos_atomicos

1. Ler limites canonicos e criterios de elegibilidade em `GOV-USER-STORY.md`
2. Criar `TEMPLATE-USER-STORY.md` com frontmatter: doc_id, version, status, owner, last_updated, task_instruction_mode, feature_id, decision_refs
3. Incluir secoes obrigatorias listadas no README da issue (espelhar estrutura de issue granularizada do `GOV-ISSUE-FIRST.md` adaptada ao nivel US)
4. Garantir placeholders claros para links a `TASK-N.md` quando a US for desdobrada em tasks
5. Verificar ausencia de termos legados inconsistentes com Feature/US/Task

## comandos_permitidos

- `rg -n "TEMPLATE-USER-STORY|User Story" PROJETOS/COMUM`
- `git diff -- PROJETOS/COMUM/TEMPLATE-USER-STORY.md`

## resultado_esperado

Template canonico utilizavel por `SESSION-PLANEJAR-PROJETO` e criacao de USs.

## testes_ou_validacoes_obrigatorias

- Confirmar que cada campo exigido na Task 2.2.1 do spec existe no template
- Confirmar coerencia com `max_tasks_por_user_story` e demais limites citados em `GOV-USER-STORY.md`

## stop_conditions

- Parar se houver conflito normativo entre spec e `GOV-USER-STORY.md`; escalar em `DECISION-PROTOCOL` ou intake derivado
