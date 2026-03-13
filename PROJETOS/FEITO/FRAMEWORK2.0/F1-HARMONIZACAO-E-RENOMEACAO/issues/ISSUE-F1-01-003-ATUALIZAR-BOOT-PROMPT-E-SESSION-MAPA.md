---
doc_id: "ISSUE-F1-01-003-ATUALIZAR-BOOT-PROMPT-E-SESSION-MAPA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-003 - Atualizar boot prompt e session mapa

## User Story

Como operador do framework, quero os entrypoints autonomo e interativo apontando
para os nomes novos para nao iniciar um fluxo ja em estado inconsistente.

## Contexto Tecnico

`boot-prompt.md` e `SESSION-MAPA.md` sao os entrypoints do framework. Um deles
apontando para nomes antigos quebra a experiencia logo no inicio do fluxo.

## Plano TDD

- Red: identificar referencias antigas nos dois entrypoints.
- Green: alinhar o boot prompt ao conjunto novo e consolidar o mapa de sessao.
- Refactor: revisar links, nomes e escopo de cada modo de operacao.

## Criterios de Aceitacao

- Given o modo autonomo, When `boot-prompt.md` for lido, Then o Nivel 2 referencia apenas os nomes novos de governanca
- Given o modo interativo, When `SESSION-MAPA.md` for lido, Then todos os prompts de sessao listados usam os nomes finais
- Given os dois entrypoints, When o PM escolher um modo, Then a diferenca entre autonomo e interativo fica clara

## Definition of Done da Issue

- [x] `boot-prompt.md` atualizado
- [x] `SESSION-MAPA.md` atualizado
- [x] nomes e diferencas operacionais coerentes entre os dois entrypoints

## Tasks Decupadas

- [x] T1: revisar o estado atual de `boot-prompt.md`
- [x] T2: revisar o estado atual de `SESSION-MAPA.md`
- [x] T3: alinhar referencias, nomes e responsabilidades dos dois entrypoints

## Instructions por Task

### T1
- objetivo: validar o papel do entrypoint autonomo
- precondicoes: renomeacao interna de `PROJETOS/COMUM/` concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/boot-prompt.md`
  - `PROJETOS/COMUM/GOV-*.md`
- passos_atomicos:
  1. revisar a lista de leitura do Nivel 2
  2. atualizar nomes antigos para os nomes finais
  3. adicionar referencia ao mapa de sessao para operacao interativa
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: `boot-prompt.md` aponta apenas para o conjunto novo de governanca
- testes_ou_validacoes_obrigatorias:
  - `rg -n "GOV-|SPEC-|SESSION-MAPA" PROJETOS/boot-prompt.md`
- stop_conditions:
  - parar se o PRD exigir mudanca de fluxo alem do Nivel 1-3

### T2
- objetivo: consolidar o entrypoint interativo
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SESSION-MAPA.md`
  - `PROJETOS/COMUM/SESSION-*.md`
- passos_atomicos:
  1. listar os prompts de sessao realmente disponiveis
  2. trocar nomes antigos pelos nomes finais
  3. alinhar a tabela de uso e o mapa de prompts ao estado real
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: `SESSION-MAPA.md` reflete os prompts finais do framework
- testes_ou_validacoes_obrigatorias:
  - `sed -n '1,120p' PROJETOS/COMUM/SESSION-MAPA.md`
- stop_conditions:
  - parar se houver prompt necessario ainda sem especificacao minima

### T3
- objetivo: garantir coerencia entre os dois modos de operacao
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/boot-prompt.md`
  - `PROJETOS/COMUM/SESSION-MAPA.md`
  - `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
- passos_atomicos:
  1. revisar se autonomo e interativo estao descritos como modos complementares
  2. corrigir divergencias de nomenclatura ou de escopo
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: entrypoints coerentes entre si
- testes_ou_validacoes_obrigatorias:
  - `rg -n "SESSION-MAPA|boot-prompt" PROJETOS/COMUM/SESSION-MAPA.md PROJETOS/boot-prompt.md`
- stop_conditions:
  - parar se a coerencia depender de prompt ainda nao criado e fora do epic

## Arquivos Reais Envolvidos

- `PROJETOS/boot-prompt.md`
- `PROJETOS/COMUM/SESSION-MAPA.md`
- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`

## Artifact Minimo

- `PROJETOS/boot-prompt.md`

## Dependencias

- [Issue 002](./ISSUE-F1-01-002-RENOMEAR-ARQUIVOS-DE-COMUM-E-ALINHAR-REFERENCIAS-INTERNAS.md)
- [Epic](../EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
