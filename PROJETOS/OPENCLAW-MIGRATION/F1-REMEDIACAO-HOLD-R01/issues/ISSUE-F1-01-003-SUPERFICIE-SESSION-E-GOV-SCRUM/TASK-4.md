---
doc_id: "TASK-4.md"
issue_id: "ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM"
task_id: "T4"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T4 - Alinhar SESSION-IMPLEMENTAR-US a GOV-USER-STORY

## objetivo

Incluir referencia explicita a `GOV-USER-STORY.md` como fonte de limites de tamanho e elegibilidade da US (verificacao cruzada do relatorio R01).

## precondicoes

- `GOV-USER-STORY.md` presente em COMUM

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/COMUM/GOV-USER-STORY.md`

## passos_atomicos

1. Identificar secao de leitura obrigatoria ou pre-requisitos
2. Adicionar bullet com path canónico para limites (`max_tasks_por_user_story`, etc.)
3. Garantir que nenhuma instrucao contradiz esses limites

## comandos_permitidos

- `rg -n "GOV-USER-STORY" PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`

## resultado_esperado

Pelo menos uma referencia clara a `GOV-USER-STORY.md` no corpo do SESSION.

## testes_ou_validacoes_obrigatorias

- `rg` confirma ocorrencia de `GOV-USER-STORY`

## stop_conditions

- Parar se o SESSION estiver vazio ou nao legivel
