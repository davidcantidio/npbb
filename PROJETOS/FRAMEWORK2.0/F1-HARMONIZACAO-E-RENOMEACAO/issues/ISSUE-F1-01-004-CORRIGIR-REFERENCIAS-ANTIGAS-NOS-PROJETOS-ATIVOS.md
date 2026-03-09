---
doc_id: "ISSUE-F1-01-004-CORRIGIR-REFERENCIAS-ANTIGAS-NOS-PROJETOS-ATIVOS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-004 - Corrigir referencias antigas nos projetos ativos

## User Story

Como operador do framework, quero os projetos ativos navegando pelos nomes novos
para nao deixar o backlog atual dependente de arquivos removidos.

## Contexto Tecnico

Mesmo com `PROJETOS/COMUM/` renomeado, os projetos ativos ainda podem citar
nomes antigos em issues, audit logs e prompts locais. A ordem da correcao e critica.

## Plano TDD

- Red: localizar referencias antigas nos projetos ativos.
- Green: corrigir `FRAMEWORK2.0`, `PILOTO-ISSUE-FIRST` e `dashboard-leads-etaria`.
- Refactor: revisar se restaram referencias obrigatorias antigas.

## Criterios de Aceitacao

- Given os projetos ativos, When a issue for concluida, Then os links obrigatorios para `COMUM` apontam para os nomes novos
- Given `FRAMEWORK2.0`, When o prompt local de planejamento for lido, Then ele aponta para `PROMPT-PLANEJAR-FASE.md` e para um `PRD_PATH` valido
- Given `PILOTO-ISSUE-FIRST` e `dashboard-leads-etaria`, When seus artefatos comuns forem lidos, Then nao dependem de nomes antigos de governanca

## Definition of Done da Issue

- [x] referencias obrigatorias corrigidas em `FRAMEWORK2.0`
- [x] referencias obrigatorias corrigidas em `PILOTO-ISSUE-FIRST`
- [x] referencias obrigatorias corrigidas em `dashboard-leads-etaria`

## Tasks Decupadas

- [x] T1: revisar referencias antigas em `FRAMEWORK2.0`
- [x] T2: revisar referencias antigas em `PILOTO-ISSUE-FIRST`
- [x] T3: revisar referencias antigas em `dashboard-leads-etaria`
- [x] T4: executar validacao final nos projetos ativos

## Instructions por Task

### T1
- objetivo: corrigir os artefatos ativos do proprio projeto `FRAMEWORK2.0`
- precondicoes: nomes finais de `PROJETOS/COMUM/` ja existentes
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/SESSION-PLANEJAR-PROJETO-Projeto-completo.md`
  - `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0.md`
- passos_atomicos:
  1. corrigir referencias obrigatorias de navegacao e exemplos operacionais
  2. manter no PRD as mencoes historicas necessarias para a critica, sem reescrever a analise
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: artefatos ativos de `FRAMEWORK2.0` usam os nomes novos onde houver referencia operacional
- testes_ou_validacoes_obrigatorias:
  - `rg -n "COMUM/(SCRUM-GOV|INTAKE-FRAMEWORK|AUDITORIA-GOV|prompt_epicos_issues)" PROJETOS/FRAMEWORK2.0`
- stop_conditions:
  - parar se a correcao apagar mencao historica relevante do PRD

### T2
- objetivo: corrigir o piloto ativo
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/PILOTO-ISSUE-FIRST/DECISION-PROTOCOL.md`
  - `PROJETOS/PILOTO-ISSUE-FIRST/F1-VALIDACAO-DO-FRAMEWORK/issues/`
  - `PROJETOS/PILOTO-ISSUE-FIRST/feito/README.md`
- passos_atomicos:
  1. atualizar referencias do piloto para `GOV-DECISOES`, `GOV-SCRUM`, `GOV-ISSUE-FIRST`, `GOV-SPRINT-LIMITES` e `GOV-WORK-ORDER`
  2. preservar o conteudo funcional do piloto
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: piloto navega pelos nomes finais
- testes_ou_validacoes_obrigatorias:
  - `rg -n "COMUM/(SCRUM-GOV|ISSUE-FIRST-TEMPLATES|SPRINT-LIMITS|WORK-ORDER-SPEC|DECISION-PROTOCOL)" PROJETOS/PILOTO-ISSUE-FIRST`
- stop_conditions:
  - parar se uma referencia local nao representar o documento comum correspondente

### T3
- objetivo: corrigir o projeto ativo `dashboard-leads-etaria`
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/dashboard-leads-etaria/DECISION-PROTOCOL.md`
  - `PROJETOS/dashboard-leads-etaria/AUDIT-LOG.md`
- passos_atomicos:
  1. atualizar referencias para `GOV-DECISOES` e `GOV-AUDITORIA`
  2. preservar trilha de auditoria ja consolidada
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: dashboard ativo referencia o conjunto novo de governanca
- testes_ou_validacoes_obrigatorias:
  - `rg -n "COMUM/(AUDITORIA-GOV|DECISION-PROTOCOL)" PROJETOS/dashboard-leads-etaria`
- stop_conditions:
  - parar se a correcao exigir reescrever relatorios auditados

### T4
- objetivo: validar que os projetos ativos criticos nao dependem mais dos nomes antigos
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/`
  - `PROJETOS/PILOTO-ISSUE-FIRST/`
  - `PROJETOS/dashboard-leads-etaria/`
- passos_atomicos:
  1. executar busca final por nomes antigos do conjunto comum
  2. revisar os residuos e manter apenas mencoes historicas deliberadas
- comandos_permitidos:
  - `rg`
- resultado_esperado: referencias obrigatorias dos projetos ativos corrigidas
- testes_ou_validacoes_obrigatorias:
  - `rg -n "COMUM/(scrum-framework-master\\.md|SCRUM-GOV\\.md|SPRINT-LIMITS\\.md|WORK-ORDER-SPEC\\.md|ISSUE-FIRST-TEMPLATES\\.md|TASK_INSTRUCTIONS_SPEC\\.md|INTAKE-FRAMEWORK\\.md|AUDITORIA-GOV\\.md|DECISION-PROTOCOL\\.md|prompt_epicos_issues\\.md)" PROJETOS/FRAMEWORK2.0 PROJETOS/PILOTO-ISSUE-FIRST PROJETOS/dashboard-leads-etaria`
- stop_conditions:
  - parar se restarem apenas mencoes historicas em PRDs que nao devam ser alteradas

## Arquivos Reais Envolvidos

- `PROJETOS/FRAMEWORK2.0/`
- `PROJETOS/PILOTO-ISSUE-FIRST/`
- `PROJETOS/dashboard-leads-etaria/`

## Artifact Minimo

- `PROJETOS/FRAMEWORK2.0/SESSION-PLANEJAR-PROJETO-Projeto-completo.md`

## Dependencias

- [Issue 003](./ISSUE-F1-01-003-ATUALIZAR-BOOT-PROMPT-E-SESSION-MAPA.md)
- [Epic](../EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
