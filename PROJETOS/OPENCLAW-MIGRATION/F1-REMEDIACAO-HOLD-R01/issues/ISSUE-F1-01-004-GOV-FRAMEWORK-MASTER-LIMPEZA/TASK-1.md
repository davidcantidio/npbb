---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA"
task_id: "T1"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
tdd_aplicavel: false
---

# T1 - Limpar GOV-FRAMEWORK-MASTER

## objetivo

Remover `issue-first` e referencias operacionais a fase fora de bloco `deprecated`, mantendo apenas ponteiros de compatibilidade onde necessario, conforme B4 do R01.

## precondicoes

- Ler SCOPE-DRIFT A-04 no relatorio R01
- Confirmar nome canónico do documento de auditoria de feature em `PROJETOS/COMUM/`

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md`
- `PROJETOS/OPENCLAW-MIGRATION/openclaw-migration-spec.md` (US-1.1)

## passos_atomicos

1. Localizar mencoes a `issue-first`, arquivamento de fase, Sprint, Epico
2. Reescrever paragrafo de padrao do repositório para Feature/US/Task
3. Isolar qualquer texto necessário sobre estrutura legada em secao explicitamente titulada para compatibilidade
4. Resolver referencia `GOV-AUDITORIA-FEATURE.md` vs expectativa do PRD com nota de fonte de verdade se arquivos divergirem
5. Cruzar com `boot-prompt.md` apos ISSUE-F1-01-002 para consistencia de paths

## comandos_permitidos

- `rg -n "issue-first|Fase|Épico|Sprint|arquivamento" PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `ls PROJETOS/COMUM/GOV-AUDITORIA*.md`

## resultado_esperado

Master como mapa de alto nivel sem contaminacao legada na leitura principal.

## testes_ou_validacoes_obrigatorias

- Leitura das primeiras seccoes nao sugere issue-first como modelo activo

## stop_conditions

- Parar se remocao de `issue-first` conflitar com `AGENTS.md` ou regras de workspace; alinhar ambos numa unica decisao documentada
