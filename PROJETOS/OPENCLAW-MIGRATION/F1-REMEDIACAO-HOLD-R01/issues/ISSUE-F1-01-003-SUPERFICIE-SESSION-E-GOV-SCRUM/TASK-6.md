---
doc_id: "TASK-6.md"
issue_id: "ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM"
task_id: "T6"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T6 - Depreciar SESSIONs legados

## objetivo

Marcar `SESSION-IMPLEMENTAR-ISSUE.md`, `SESSION-AUDITAR-FASE.md` e `SESSION-REVISAR-ISSUE.md` como `status: deprecated` no frontmatter, com ponteiro explicito para o substituto.

## precondicoes

- T1 e T3 concluidas para que os substitutos existam e estejam referenciados

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- `PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/COMUM/SESSION-REVISAR-US.md`

## passos_atomicos

1. Actualizar frontmatter `status: deprecated` e `last_updated`
2. Acrescentar bloco curto no topo do corpo: substituto canónico e motivo
3. Garantir que `SESSION-MAPA.md` nao lista estes como `active` (coordenar com T2)

## comandos_permitidos

- `rg -n "status:" PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md PROJETOS/COMUM/SESSION-AUDITAR-FASE.md PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md`

## resultado_esperado

Tres ficheiros legados claramente depreciados sem remocao fisica.

## testes_ou_validacoes_obrigatorias

- Cada ficheiro contem ponteiro para substituto US/Feature

## stop_conditions

- Parar se politica do repo exigir manter `active` por compatibilidade; documentar excepcao no AUDIT-LOG
