---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM"
task_id: "T3"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T3 - Corrigir SESSION-AUDITAR-FEATURE.md

## objetivo

Eliminar regressao ao fluxo ISSUE no bloco de bloqueio por follow-up (ACHADO A-06): referencias a `SESSION-IMPLEMENTAR-ISSUE.md` e `SESSION-REVISAR-ISSUE.md` devem apontar para US/Feature.

## precondicoes

- Ler achado A-06 no relatorio R01

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/COMUM/SESSION-REVISAR-US.md`
- `PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md`

## passos_atomicos

1. Localizar bloco nas linhas indicadas no relatorio (~190-195) ou equivalente actual
2. Substituir referencias por SESSION-IMPLEMENTAR-US e SESSION-REVISAR-US
3. Revalidar restantes referencias no ficheiro para coerencia com auditoria de Feature

## comandos_permitidos

- `rg -n "IMPLEMENTAR-ISSUE|REVISAR-ISSUE|AUDITAR-FASE" PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`

## resultado_esperado

Auditoria de Feature nao reintroduz o ciclo issue-first nos follow-ups.

## testes_ou_validacoes_obrigatorias

- Nenhuma ocorrencia activa de encaminhamento para ISSUE nos passos de remediacao pos-hold

## stop_conditions

- Parar se o template referenciado (`TEMPLATE-AUDITORIA-FEATURE.md`) estiver ausente
