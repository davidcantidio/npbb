---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T1 - Reescrever boot-prompt niveis 4-6

## objetivo

Substituir a descoberta `Fase > Epico > Issue` pela cadeia `Feature > User Story > Task` em `boot-prompt.md`, incluindo quadro de confirmacao e fluxos de auditoria/fechamento coerentes com o PRD da migracao.

## precondicoes

- Ler `GOV-FRAMEWORK-MASTER.md` para estrutura de pastas e artefactos
- Ler Task 3.1.1 em `openclaw-migration-spec.md`

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/boot-prompt.md`
- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/OPENCLAW-MIGRATION/openclaw-migration-spec.md`
- `PROJETOS/COMUM/SESSION-MAPA.md` (consistencia pos ISSUE-F1-01-003)

## passos_atomicos

1. Mapear niveis 4-6 actuais e todas as referencias a Fase/Epico/Issue/Sprint
2. Redigir algoritmo de descoberta: Feature activa -> US elegivel -> Task `todo`/`active`
3. Actualizar quadro de confirmacao (MODO, PROJETO, FEATURE ALVO, US ALVO, TASK ALVO, TASK_INSTR_MODE, SP, DEPENDENCIAS, DECISAO)
4. Actualizar sequencias minimas: execucao US; auditoria Feature; remediar hold
5. Conferir niveis 1-3 inalterados salvo referencias cruzadas estritamente necessarias
6. Marcar qualquer texto legado remanescente como `deprecated` com ponteiro ao substituto

## comandos_permitidos

- `rg -n "Fase|Epico|Issue|Sprint|Nível [456]" PROJETOS/COMUM/boot-prompt.md`
- `git diff -- PROJETOS/COMUM/boot-prompt.md`

## resultado_esperado

Boot autonomo operacional na hierarquia Feature/US/Task sem violar invariantes do PRD.

## testes_ou_validacoes_obrigatorias

- Percorrer mentalmente (ou simular) o boot com um projecto exemplo e verificar que nao ha dependencia de `ISSUE-` como unidade de descoberta nos niveis 4-6
- Verificar que modo AUDITORIA aponta para fluxo de Feature (SESSION-AUDITAR-FEATURE) e nao Fase

## stop_conditions

- Parar se `GOV-FRAMEWORK-MASTER.md` ainda nao definir estrutura alvo; executar ou coordenar com ISSUE-F1-01-004 antes de concluir
