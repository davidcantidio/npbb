---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM"
task_id: "T2"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T2 - Corrigir SESSION-MAPA.md

## objetivo

Alinhar `SESSION-MAPA.md` aos prompts activos reais e a nomenclatura Feature/US/Task; remover referencia a `SESSION-REVISAR-US.md` inexistente antes desta remediacao ou marcar estado correcto apos T1.

## precondicoes

- T1 concluida ou em draft aceitavel para link

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/SESSION-MAPA.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/COMUM/SESSION-REVISAR-US.md`

## passos_atomicos

1. Listar todos os SESSION-* referenciados como `active`
2. Corrigir linhas que apontam para ficheiros inexistentes
3. Para prompts substituidos, apontar para o novo ficheiro ou para entrada `deprecated` coerente com T6
4. Actualizar gatilhos rapidos e tabela comparativa boot vs SESSION

## comandos_permitidos

- `ls PROJETOS/COMUM/SESSION-*.md`
- `rg -n "status:|SESSION-" PROJETOS/COMUM/SESSION-MAPA.md`

## resultado_esperado

MAPA sem prometer ficheiros inexistentes; estado `active` apenas para prompts vigentes.

## testes_ou_validacoes_obrigatorias

- Cada link `active` resolve para ficheiro existente

## stop_conditions

- Parar se houver conflito com skills `.codex`; registrar follow-up
