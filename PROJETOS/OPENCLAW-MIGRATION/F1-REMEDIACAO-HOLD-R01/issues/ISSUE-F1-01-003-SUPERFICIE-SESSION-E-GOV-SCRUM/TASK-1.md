---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T1 - Criar SESSION-REVISAR-US.md

## objetivo

Criar `PROJETOS/COMUM/SESSION-REVISAR-US.md` como substituto operacional do fluxo de revisao pos-issue ao nivel de User Story.

## precondicoes

- Ler `SESSION-REVISAR-ISSUE.md` como base lexical
- Ler spec US de migracao e `GOV-SCRUM.md` (secao de review)

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md` (referencia cruzada)
- `PROJETOS/COMUM/SESSION-REVISAR-US.md` (criar)

## passos_atomicos

1. Copiar estrutura do SESSION-REVISAR-ISSUE adaptando termos Issue->US, paths US
2. Definir parametros de entrada (FEATURE_ID, US_PATH, etc.) coerentes com issue-first em `PROJETOS/`
3. Garantir handoff e evidencias alinhados a `GOV-SCRUM.md` pos-actualizacao (T5)
4. Incluir referencias normativas a `GOV-USER-STORY.md` onde couber

## comandos_permitidos

- `rg -n "REVISAR-ISSUE|REVISAR-US" PROJETOS/COMUM`

## resultado_esperado

Ficheiro novo versionado e referenciavel pelo MAPA na T2.

## testes_ou_validacoes_obrigatorias

- Verificar que o ficheiro existe e tem frontmatter completo
- Verificar ausencia de instrucoes que exijam `ISSUE-` como unidade de revisao

## stop_conditions

- Parar se nao existir base legivel em `SESSION-REVISAR-ISSUE.md`
