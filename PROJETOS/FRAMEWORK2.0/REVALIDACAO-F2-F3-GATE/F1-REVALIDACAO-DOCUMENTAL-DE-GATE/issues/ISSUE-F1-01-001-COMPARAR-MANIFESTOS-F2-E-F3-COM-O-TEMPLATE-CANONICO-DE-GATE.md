---
doc_id: "ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-10"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Comparar manifestos F2 e F3 com o template canonico de gate

## User Story

Como mantenedor do sibling `REVALIDACAO-F2-F3-GATE`, quero comparar os
manifestos F2 e F3 com o template canonico para saber exatamente se existe
drift de checklist/gate ou se cada manifesto ja esta aderente.

## Contexto Tecnico

O PRD derivado parte da hipotese de que F2 e F3 ainda usam a forma agregada
`pending -> hold/approved`, mas a trilha so pode avancar com evidencia atual. A
baseline precisa confirmar, por manifesto, se o delta permanece restrito ao
checklist/gate. Qualquer divergencia fora desse envelope deve bloquear a trilha
antes que `F2_FRAMEWORK2_0_EPICS.md` ou `F3_FRAMEWORK2_0_EPICS.md` sejam
tocados.

## Plano TDD

- Red: comparar template e manifestos reais sem assumir que o delta continua o mesmo do PRD
- Green: classificar cada manifesto como `drift confirmado` ou `no-op controlado`
- Refactor: explicitar o envelope permitido de ajuste para as issues seguintes

## Criterios de Aceitacao

- Given o template canonico e os manifestos F2/F3, When a comparacao for executada, Then cada manifesto recebe classificacao explicita de `drift confirmado` ou `no-op controlado`
- Given uma divergencia fora de checklist/gate, When ela for encontrada, Then a issue responde `BLOQUEADO` antes de qualquer patch em F2/F3
- Given a baseline concluida, When as issues seguintes forem lidas, Then fica claro se F2 e F3 exigem patch minimo ou apenas evidencia de aderencia

## Definition of Done da Issue

- [ ] existe delta objetivo por manifesto
- [ ] a classificacao final de F2 esta explicita
- [ ] a classificacao final de F3 esta explicita
- [ ] o envelope permitido de ajuste para as proximas issues foi delimitado
- [ ] existe stop condition explicita para drift fora de checklist/gate

## Tasks Decupadas

- [ ] T1: revisar o template canonico e as invariantes do PRD derivado
- [ ] T2: comparar F2 e F3 e classificar cada manifesto
- [ ] T3: consolidar a baseline rastreavel para as issues de ajuste

## Instructions por Task

### T1
- objetivo: identificar exatamente quais campos e quais trechos de checklist sao canonicamente esperados
- precondicoes:
  - [PRD Derivado](../../../PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md) lido
  - entendimento claro de que o sibling nao pode simular auditoria formal
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
  - `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md`
  - `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`
- passos_atomicos:
  1. localizar no template canonico o bloco de checklist com `not_ready -> pending`, `pending -> hold` e `pending -> approved`
  2. listar as invariantes do PRD derivado que nao podem ser violadas durante esta trilha
  3. registrar na propria issue quais campos das fases F2/F3 podem ser analisados e quais nao podem ser alterados
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: baseline com lista objetiva de invariantes e faixa permitida de comparacao
- testes_ou_validacoes_obrigatorias:
  - `rg -n "pending -> hold|pending -> approved|audit_gate|gate_atual|ultima_auditoria" PROJETOS/COMUM/GOV-ISSUE-FIRST.md PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE\\ 1.md`
- stop_conditions:
  - parar se o PRD derivado exigir alterar qualquer campo fora de checklist/gate
  - parar se o template canonico nao estiver claro o suficiente para comparar os manifestos

### T2
- objetivo: comparar o estado atual de F2 e F3 com o template e classificar o delta por manifesto
- precondicoes:
  - T1 concluida
  - invariantes da comparacao registradas
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`
- passos_atomicos:
  1. comparar o bloco de checklist de F2 com o template e anotar se ha `drift confirmado` ou `no-op controlado`
  2. comparar o bloco de checklist de F3 com o template e anotar se ha `drift confirmado` ou `no-op controlado`
  3. verificar se existe qualquer divergencia fora de checklist/gate e, se existir, marcar a trilha como `BLOQUEADO`
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: classificacao objetiva de F2 e F3, com bloqueio imediato se surgir drift fora do escopo
- testes_ou_validacoes_obrigatorias:
  - `rg -n "pending -> hold/approved|pending -> hold|pending -> approved" PROJETOS/FRAMEWORK2.0/F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
- stop_conditions:
  - parar se `status`, `audit_gate`, `gate_atual` ou `ultima_auditoria` de F2/F3 precisarem ser reinterpretados para fechar a baseline
  - parar se a divergencia envolver epicos, issues, DoD ou dependencias funcionais

### T3
- objetivo: transformar a comparacao em baseline operavel para as issues de ajuste
- precondicoes:
  - T2 concluida
  - classificacao final de F2 e F3 definida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`
  - `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/EPIC-F1-01-BASELINE-DE-ADERENCIA-F2-F3-VS-TEMPLATE-CANONICO.md`
- passos_atomicos:
  1. registrar na issue, de forma curta, se F2 exige patch minimo ou no-op controlado
  2. registrar na issue, de forma curta, se F3 exige patch minimo ou no-op controlado
  3. explicitar que qualquer achado fora de checklist/gate bloqueia `ISSUE-F1-02-001` e `ISSUE-F1-02-002`
- comandos_permitidos:
  - `apply_patch`
  - `rg`
- resultado_esperado: baseline rastreavel e diretamente consumivel pelas issues de ajuste
- testes_ou_validacoes_obrigatorias:
  - `rg -n "drift confirmado|no-op controlado|BLOQUEADO" PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`
- stop_conditions:
  - parar se a baseline depender de criar arquivo auxiliar fora do backlog aprovado
  - parar se a evidenca final exigir simular auditoria ou atualizar `AUDIT-LOG.md`

## Baseline Canonica e Envelope da Comparacao

### Contrato canonico confirmado

- o template canonico de fase exige tres blocos distintos em `## Checklist de Transicao de Gate`: `not_ready -> pending`, `pending -> hold` e `pending -> approved`
- o template canonico exige `audit_gate: "not_ready"` no frontmatter e estado pre-auditoria explicito com `gate_atual: not_ready` e `ultima_auditoria: nao_aplicavel`
- o PRD derivado limita esta trilha a remediacao documental minima e proibe alterar backlog funcional, `AUDIT-LOG.md`, relatorios de auditoria ou qualquer estado de fase fora do trecho de checklist/gate

### Faixa permitida de comparacao nesta issue

- pode analisar: bloco de checklist/gate, `audit_gate`, `gate_atual` e `ultima_auditoria` apenas para confirmar aderencia pre-auditoria
- pode registrar: classificacao `drift confirmado` ou `no-op controlado` por manifesto e a necessidade de `patch minimo` nas issues seguintes
- nao pode alterar: `status`, `audit_gate`, `gate_atual`, `ultima_auditoria`, objetivo da fase, tabela de epicos, dependencias, escopo, DoD, `AUDIT-LOG.md` ou qualquer artefato de auditoria
- stop condition ativa: qualquer achado que exija reinterpretar campos fora de checklist/gate bloqueia esta trilha como `BLOQUEADO`

## Resultado da Comparacao

### F2 - `F2_FRAMEWORK2_0_EPICS.md`

- classificacao final: `drift confirmado`
- delta objetivo: o manifesto ainda usa o bloco agregado `pending -> hold/approved`, enquanto o template canonico exige dois blocos separados: `pending -> hold` e `pending -> approved`
- verificacao de invariantes: `audit_gate` permanece `not_ready`, `gate_atual` permanece `not_ready` e `ultima_auditoria` permanece `nao_aplicavel`
- leitura operacional: `status: active` reflete progresso real da fase e nao precisou ser reinterpretado para fechar a baseline
- encaminhamento: F2 exige `patch minimo` restrito ao split do checklist/gate; nao houve evidencia de drift adicional em epicos, issues, DoD ou dependencias funcionais dentro do envelope desta issue

### F3 - `F3_FRAMEWORK2_0_EPICS.md`

- classificacao final: `drift confirmado`
- delta objetivo: o manifesto ainda usa o bloco agregado `pending -> hold/approved`, enquanto o template canonico exige dois blocos separados: `pending -> hold` e `pending -> approved`
- verificacao de invariantes: `audit_gate` permanece `not_ready`, `gate_atual` permanece `not_ready` e `ultima_auditoria` permanece `nao_aplicavel`
- leitura operacional: `status: todo` reflete o estado atual da fase e nao precisou ser reinterpretado para fechar a baseline
- encaminhamento: F3 exige `patch minimo` restrito ao split do checklist/gate; nao houve evidencia de drift adicional em epicos, issues, DoD ou dependencias funcionais dentro do envelope desta issue

## Baseline Operavel para as Issues Seguintes

- `ISSUE-F1-02-001` deve tratar F2 como `patch minimo`, replicando o split canonico `pending -> hold` e `pending -> approved` sem tocar nenhum outro campo do manifesto
- `ISSUE-F1-02-002` deve tratar F3 como `patch minimo`, replicando o split canonico `pending -> hold` e `pending -> approved` sem tocar nenhum outro campo do manifesto
- `no-op controlado` nao se aplica nesta baseline porque F2 e F3 ainda nao estao aderentes ao checklist split do template
- se qualquer issue seguinte encontrar achado fora de checklist/gate, a execucao deve responder `BLOQUEADO` antes de editar F2 ou F3
- esta baseline nao autoriza simular auditoria formal, criar `RELATORIO-AUDITORIA-F2-R01.md` ou `RELATORIO-AUDITORIA-F3-R01.md`, nem atualizar `AUDIT-LOG.md`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/FRAMEWORK2.0/F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md`
- `PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
- `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md`

## Artifact Minimo

- `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`

## Dependencias

- [Intake Derivado](../../../INTAKE-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md)
- [PRD Derivado](../../../PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md)
- [Epic](../EPIC-F1-01-BASELINE-DE-ADERENCIA-F2-F3-VS-TEMPLATE-CANONICO.md)
- [Fase](../F1_REVALIDACAO_F2_F3_GATE_EPICS.md)
- [F2](../../../F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md)
- [F3](../../../F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md)
