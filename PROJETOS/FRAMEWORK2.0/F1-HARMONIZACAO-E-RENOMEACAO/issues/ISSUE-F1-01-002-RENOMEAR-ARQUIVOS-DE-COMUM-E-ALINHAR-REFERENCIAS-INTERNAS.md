---
doc_id: "ISSUE-F1-01-002-RENOMEAR-ARQUIVOS-DE-COMUM-E-ALINHAR-REFERENCIAS-INTERNAS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-002 - Renomear arquivos de COMUM e alinhar referencias internas

## User Story

Como responsavel pelo framework, quero renomear os artefatos comuns e alinhar as
referencias internas para que o namespace comum passe a comunicar funcao por prefixo.

## Contexto Tecnico

Esta issue executa a renomeacao principal de `PROJETOS/COMUM/`. O risco e alto
porque qualquer ordem errada deixa o framework comum inconsistente ou com links quebrados.

## Plano TDD

- Red: localizar referencias internas ainda usando nomes antigos.
- Green: renomear os arquivos e ajustar os documentos comuns para os nomes finais.
- Refactor: revisar doc_id, titulos e referencias normativas apos a renomeacao.

## Criterios de Aceitacao

- Given os arquivos comuns antigos, When a renomeacao for concluida, Then todos os artefatos de `PROJETOS/COMUM/` usam prefixos funcionais
- Given os documentos comuns renomeados, When forem lidos, Then `doc_id`, titulo e referencias internas apontam para os nomes novos
- Given o framework comum, When for feita busca por nomes antigos em `PROJETOS/COMUM/`, Then nao restam referencias normativas ativas

## Definition of Done da Issue

- [x] arquivos renomeados fisicamente
- [x] referencias internas corrigidas
- [x] doc_id e titulos alinhados aos nomes finais

## Tasks Decupadas

- [x] T1: aplicar a renomeacao fisica dos arquivos de `PROJETOS/COMUM/`
- [x] T2: alinhar `doc_id`, titulos e referencias internas dos arquivos renomeados
- [x] T3: criar os novos artefatos faltantes do conjunto comum
- [x] T4: verificar ausencia de referencias antigas restantes em `PROJETOS/COMUM/`

## Instructions por Task

### T1
- objetivo: executar a renomeacao fisica da arvore comum
- precondicoes: mapa de renomeacao aprovado pela issue anterior
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/`
- passos_atomicos:
  1. renomear os arquivos alvo para os nomes finais com prefixos `GOV-`, `TEMPLATE-`, `PROMPT-`, `SESSION-` e `SPEC-`
  2. garantir que nenhum nome antigo permaneceu em `PROJETOS/COMUM/`
- comandos_permitidos:
  - `mv`
  - `rg`
- resultado_esperado: arvore comum com os nomes finais em disco
- testes_ou_validacoes_obrigatorias:
  - `rg --files PROJETOS/COMUM`
- stop_conditions:
  - parar se houver colisao de nome ou arquivo faltante fora do mapa aprovado

### T2
- objetivo: alinhar metadados e referencias internas apos a renomeacao
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/GOV-*.md`
  - `PROJETOS/COMUM/TEMPLATE-*.md`
  - `PROJETOS/COMUM/PROMPT-*.md`
  - `PROJETOS/COMUM/SESSION-*.md`
  - `PROJETOS/COMUM/SPEC-*.md`
- passos_atomicos:
  1. atualizar `doc_id` e titulos que ainda refletirem o nome antigo
  2. corrigir referencias internas entre os documentos comuns
  3. remover duplicacao normativa onde o plano exigir fonte unica
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: documentos comuns coerentes entre si e com nomes finais
- testes_ou_validacoes_obrigatorias:
  - `rg -n "SCRUM-GOV|INTAKE-FRAMEWORK|AUDITORIA-GOV|ISSUE-FIRST-TEMPLATES" PROJETOS/COMUM`
- stop_conditions:
  - parar se a remocao de duplicacao exigir decisao de escopo fora do PRD

### T3
- objetivo: criar os artefatos novos previstos no plano
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
  - `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
  - `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
  - `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
  - `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
  - `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`
- passos_atomicos:
  1. criar cada arquivo novo com frontmatter e objetivo compativeis com o PRD
  2. adicionar referencias cruzadas minimas entre os novos artefatos e a governanca
- comandos_permitidos:
  - `apply_patch`
- resultado_esperado: conjunto comum completo segundo o mapa final
- testes_ou_validacoes_obrigatorias:
  - `find PROJETOS/COMUM -maxdepth 1 -type f | sort`
- stop_conditions:
  - parar se algum artefato novo demandar regra ausente no PRD

### T4
- objetivo: validar que o namespace comum ficou limpo
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/`
- passos_atomicos:
  1. buscar nomes antigos remanescentes em `PROJETOS/COMUM/`
  2. corrigir os residuos ainda ativos
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: nenhuma referencia normativa antiga ativa em `PROJETOS/COMUM/`
- testes_ou_validacoes_obrigatorias:
  - `rg -n "scrum-framework-master.md|SCRUM-GOV.md|SPRINT-LIMITS.md|WORK-ORDER-SPEC.md|ISSUE-FIRST-TEMPLATES.md|TASK_INSTRUCTIONS_SPEC.md|INTAKE-FRAMEWORK.md|AUDITORIA-GOV.md|AUDITORIA-REPORT-TEMPLATE.md|AUDITORIA-LOG-TEMPLATE.md|prompt_epicos_issues.md" PROJETOS/COMUM`
- stop_conditions:
  - parar se restar apenas mencao historica deliberada que nao deva ser removida

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`

## Dependencias

- [Issue 001](./ISSUE-F1-01-001-INVENTARIAR-MAPA-DE-RENOMEACAO-E-IMPACTO-EM-PROJETOS-ATIVOS.md)
- [Epic](../EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
