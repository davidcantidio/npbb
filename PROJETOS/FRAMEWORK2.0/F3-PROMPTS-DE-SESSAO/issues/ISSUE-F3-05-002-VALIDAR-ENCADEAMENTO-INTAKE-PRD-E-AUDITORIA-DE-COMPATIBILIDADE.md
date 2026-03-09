---
doc_id: "ISSUE-F3-05-002-VALIDAR-ENCADEAMENTO-INTAKE-PRD-E-AUDITORIA-DE-COMPATIBILIDADE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-05-002 - Validar encadeamento intake PRD e auditoria de compatibilidade

## User Story

Como mantenedor do framework, quero validar que a remediacao de monolito se
encaixa no encadeamento `intake -> PRD -> fases -> issues -> auditoria`.

## Contexto Tecnico

Esta issue fecha a compatibilidade sistemica do novo fluxo de refatoracao
estrutural. O objetivo nao e criar novos artefatos, mas provar que os prompts
de sessao e a governanca se encadeiam sem lacunas operacionais.

## Plano TDD

- Red: mapear pontos de quebra entre o intake estrutural e o fluxo canonico.
- Green: alinhar os prompts e referencias cruzadas para fechar o encadeamento.
- Refactor: revisar se nao surgiram novas regras fora do PRD.

## Criterios de Aceitacao

- Given o fluxo de remediacao estrutural, When for lido do intake ate a
  auditoria, Then cada transicao aponta para um artefato existente
- Given os prompts de sessao envolvidos, When forem comparados, Then nenhum
  deles exige pular etapa do fluxo canonico
- Given a compatibilidade validada, When um PM iniciar uma remediacao de
  monolito, Then o caminho operacional esta fechado sem improviso

## Definition of Done da Issue

- [ ] encadeamento canonico validado ponta a ponta
- [ ] referencias cruzadas coerentes entre prompts e governanca
- [ ] nenhuma lacuna critica sem dono residual

## Tasks Decupadas

- [ ] T1: mapear o encadeamento canonico ponta a ponta
- [ ] T2: alinhar referencias cruzadas e precondicoes
- [ ] T3: validar o fluxo final contra o PRD e a auditoria

## Instructions por Task

### T1
- objetivo: mapear o fluxo completo de remediacao estrutural dentro do framework
- precondicoes: `SESSION-REFATORAR-MONOLITO.md`, `PROMPT-MONOLITO-PARA-INTAKE.md`, `SESSION-CRIAR-PRD.md`, `SESSION-PLANEJAR-PROJETO.md` e `SESSION-IMPLEMENTAR-ISSUE.md` existentes
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
  - `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
  - `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
  - `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
  - `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
  - `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`
- passos_atomicos:
  1. listar a ordem esperada de uso dos prompts e artefatos entre intake, PRD, fases, issues e auditoria
  2. identificar precondicoes declaradas e outputs esperados em cada transicao
  3. apontar lacunas em que um prompt exija contexto nao entregue pela etapa anterior
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: mapa ponta a ponta do fluxo estrutural e suas precondicoes
- testes_ou_validacoes_obrigatorias:
  - `rg -n "SESSION-|PROMPT-MONOLITO|intake|PRD|auditoria" PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- stop_conditions:
  - parar se alguma etapa obrigatoria nao existir em artefato real

### T2
- objetivo: corrigir referencias cruzadas e precondicoes quebradas entre os prompts
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`
  - `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
  - `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
  - `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
  - `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- passos_atomicos:
  1. alinhar referencias cruzadas para que cada prompt aponte para a etapa seguinte ou previa correta
  2. registrar precondicoes minimas quando o fluxo exigir intake aprovado, PRD existente, fase gerada ou auditoria anterior
  3. remover instrucoes que permitam pular etapas sem base documental
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: prompts com handoff explicito e sem drift de fluxo
- testes_ou_validacoes_obrigatorias:
  - `rg -n "pre-cond|precond|depende|usar" PROJETOS/COMUM/SESSION-*.md`
- stop_conditions:
  - parar se o alinhamento exigir criar uma nova etapa nao prevista no PRD

### T3
- objetivo: validar a compatibilidade final contra o PRD e a governanca de auditoria
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0.md`
  - `PROJETOS/COMUM/GOV-INTAKE.md`
  - `PROJETOS/COMUM/GOV-AUDITORIA.md`
  - `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`
  - `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- passos_atomicos:
  1. revisar se o encadeamento respeita o fluxo canonico definido no PRD
  2. revisar se a auditoria continua encerrando o ciclo sem escrita automatica
  3. revisar se qualquer lacuna restante precisa ser marcada como `BLOQUEADO` e nao preenchida por inferencia
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: cadeia completa validada e coerente com o PRD
- testes_ou_validacoes_obrigatorias:
  - `rg -n "BLOQUEADO|confirm|auditoria|intake|PRD" PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- stop_conditions:
  - parar se faltar insumo no PRD para fechar alguma transicao `required`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `PROJETOS/COMUM/GOV-AUDITORIA.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`

## Dependencias

- [Issue 001](./ISSUE-F3-05-001-REDIGIR-SESSION-REFATORAR-MONOLITO-COMO-MINI-PROJETO.md)
- [Epic](../EPIC-F3-05-SESSION-REFATORAR-MONOLITO.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [F2](../../F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
