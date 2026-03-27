---
doc_id: "TASK-5.md"
issue_id: "ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM"
task_id: "T5"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T5 - Atualizar GOV-SCRUM.md

## objetivo

Remover ou isolar termos legados (`review pos-issue`, `issue` como unidade de Task Instructions, ponteiros para SESSION-REVISAR-ISSUE) conforme ACHADO A-05 e criterios da Feature 1 do spec.

## precondicoes

- Ler relatorio R01 secao A-05

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/SESSION-REVISAR-US.md`
- `PROJETOS/OPENCLAW-MIGRATION/openclaw-migration-spec.md`

## passos_atomicos

1. Localizar linhas citadas no relatorio (34-35, 142-147, 209-210) e equivalentes
2. Substituir vocabulário por User Story / revisao pos-US onde aplicavel
3. Actualizar ponteiros de SESSION para os ficheiros vigentes
4. O que for estritamente historico mover para secao `deprecated` com data e substituto

## comandos_permitidos

- `rg -n "pos-issue|\\bissue\\b|REVISAR-ISSUE" PROJETOS/COMUM/GOV-SCRUM.md`

## resultado_esperado

Cadeia principal e procedimentos de review alinhados a Feature/US/Task.

## testes_ou_validacoes_obrigatorias

- Cadeia de trabalho legivel como `Intake > PRD > Features > User Stories > Tasks` sem regressao a Sprint/Epico/Fase no ciclo operacional

## stop_conditions

- Parar se alteracao exigir decisao de produto nao coberta pelo spec; escalar
