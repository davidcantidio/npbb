---
doc_id: "PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md"
version: "0.1"
status: "draft"
intake_kind: "audit-remediation"
owner: "PM"
last_updated: "2026-03-10"
origin_intake: "INTAKE-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md"
origin_audit: "RELATORIO-AUDITORIA-F1-R01.md"
delivery_surface: "docs-governance"
---

# PRD — FRAMEWORK2.0 — Revalidacao dos Manifestos F2/F3 contra o Checklist de Gate

## Cabecalho

| Campo | Valor |
|---|---|
| Status | draft |
| Tipo | audit-remediation |
| Entrega | rascunho derivado em chat |
| Origem do intake | `INTAKE-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md` |
| Relatorio de origem | `RELATORIO-AUDITORIA-F1-R01.md` |
| Contexto adicional | `PRD-FRAMEWORK2.0.md`, `AUDIT-LOG.md` |
| Superficie afetada | docs-governance |

---

## 1. Objetivo e Contexto

Este PRD define uma remediacao controlada e minima para revalidar os manifestos
de fase F2 e F3 de FRAMEWORK2.0 contra o contrato canonico do checklist de gate.
O objetivo nao e reabrir o projeto, alterar escopo funcional das fases nem
antecipar auditorias — e sim eliminar drift documental antes que ele reapareca
em rodadas formais futuras.

A motivacao vem do follow-up nao bloqueante N1 registrado em
`RELATORIO-AUDITORIA-F1-R01.md`, depois refletido no `AUDIT-LOG.md`. O trabalho
e estritamente documental e deve manter F2 e F3 em estado pre-auditoria.

---

## 2. Problema e Evidencia

O template canonico de manifesto de fase em `GOV-ISSUE-FIRST.md` (line 74) exige
dois ramos distintos no checklist de transicao de gate:

- `pending -> hold`
- `pending -> approved`

Os manifestos atuais de `F2_FRAMEWORK2_0_EPICS.md` (line 27) e
`F3_FRAMEWORK2_0_EPICS.md` (line 27) ainda usam a forma agregada
`pending -> hold/approved`, que perde a declaracao explicita de veredito e de
estado do gate para cada desfecho.

O risco operacional e de ambiguidade futura: um agente ou PM pode interpretar o
gate corretamente por inferencia hoje, mas a leitura deixa de ser autoexplicativa,
rastreavel e alinhada ao template oficial.

---

## 3. Escopo

### Dentro

- comparar os manifestos F2 e F3 com o template canonico de fase
- confirmar se o unico delta relevante e o split do checklist ou se existe outro
  drift documental estritamente ligado a gate
- propor apenas os ajustes minimos necessarios para alinhar o checklist ao
  contrato canonico
- registrar evidencia de aderencia ou de no-op sem simular auditoria formal

### Fora

- alterar escopo funcional, dependencias, DoD, epicos ou issues de F2/F3
- mudar `audit_gate`, `gate_atual`, `ultima_auditoria` ou `status` de fase
- criar `RELATORIO-AUDITORIA-F2-R01.md` ou `RELATORIO-AUDITORIA-F3-R01.md`
- adicionar linha nova ao `AUDIT-LOG.md`
- redefinir o template canonico de gate

---

## 4. Arquitetura Afetada e Interface Documental

### Fonte de verdade

- contrato canonico: `GOV-ISSUE-FIRST.md` (line 74)
- consumidores a revalidar: `F2_FRAMEWORK2_0_EPICS.md` (line 27),
  `F3_FRAMEWORK2_0_EPICS.md` (line 27)

### Superficies nao afetadas

- backend, frontend, banco e migracoes, autenticacao, observabilidade:
  nao aplicavel

### Invariantes obrigatorios

- `gate_atual` permanece `not_ready`
- `ultima_auditoria` permanece `nao_aplicavel`
- nao surgem `RELATORIO-AUDITORIA-F2-R01.md` ou `RELATORIO-AUDITORIA-F3-R01.md`
- nao ha nova rodada no `AUDIT-LOG.md`
- nao ha ajuste de escopo funcional dos epicos ou das issues de F2/F3

---

## 5. Fase Proposta

### Fase Unica Neutra — Remediacao Documental de Gate

> Esta fase e apenas logica no PRD. Ela nao fixa novo `F<N>` no filesystem e
> existe para orientar uma execucao futura de baixa complexidade e alto controle.

#### EPIC-RDG-01 — Baseline de Aderencia F2/F3 vs Template Canonico

**Objetivo:** comparar F2 e F3 com o template canonico e produzir um delta
objetivo por manifesto.

**Resultado esperado:**
- matriz comparativa curta por documento
- confirmacao de drift confirmado ou no-op por manifesto
- identificacao explicita de que o problema e documental, nao funcional

**Criterio de aceite:**
- o delta entre template e manifestos esta descrito sem inferencia vaga
- fica claro se a divergencia se limita ao split do checklist ou se existe
  ajuste adicional de wording estritamente ligado ao gate

#### EPIC-RDG-02 — Correcao Documental Minima

**Objetivo:** limitar a futura execucao a um patch minimo, apenas onde houver
drift comprovado.

**Resultado esperado:**
- proposta de split do checklist `pending -> hold` e `pending -> approved`
- preservacao integral dos campos de estado pre-auditoria
- zero alteracao em tabelas de epicos, dependencias, DoD e escopo

**Criterio de aceite:**
- qualquer edicao proposta fica restrita ao trecho de checklist e wording de gate
- nenhuma mudanca exige reinterpretar maturidade, progresso ou prontidao de F2/F3

#### EPIC-RDG-03 — Evidencia e Encerramento Rastreavel

**Objetivo:** fechar a revalidacao de forma auditavel sem criar artefatos de
auditoria.

**Resultado esperado:**
- registro textual de drift corrigido ou no-op controlado
- justificativa explicita para nao criar relatorio de auditoria nem entrada no
  `AUDIT-LOG.md`
- encadeamento claro para eventual planejamento ou implementacao posterior

**Criterio de aceite:**
- um leitor futuro entende o que foi revalidado, por que isso nao e auditoria
  formal e quais invariantes foram preservados

---

## 6. Metricas de Sucesso

- F2 e F3 ficam aderentes ao checklist split canonico, ou sao explicitamente
  marcadas como no-op com evidencia comparativa
- a leitura de gate em F2 e F3 deixa de depender de interpretacao implicita
- nenhuma regressao ocorre em `audit_gate`, `gate_atual`, `ultima_auditoria`,
  `status` de fase, escopo ou `AUDIT-LOG.md`
- auditorias futuras de F2/F3 encontram o contrato de gate ja alinhado ao
  template

---

## 7. Riscos e Rollback Documental

### Riscos

- excecao deliberada nao documentada em F2 ou F3 ser confundida com drift
- ampliacao indevida do escopo para "aproveitar" e revisar outras partes dos
  manifestos
- simulacao acidental de auditoria formal por meio de log, relatorio ou mudanca
  de estado

### Mitigacoes

- exigir evidencia comparativa antes de qualquer alteracao
- bloquear qualquer edicao fora da secao de checklist/gate
- tratar `PRD-FRAMEWORK2.0.md` e `AUDIT-LOG.md` apenas como contexto

### Rollback

- se a execucao futura tocar qualquer campo fora do checklist/gate, a mudanca
  deve ser revertida e reclassificada como escopo indevido
- se for encontrada evidencia de que um manifesto ja esta aderente, o fluxo
  fecha como no-op e nao edita por editar
- se surgir excecao real ao template, o trabalho deve parar com registro da
  divergencia, nao com "correcao" presumida

---

## 8. Criterios de Validacao e Cenarios

### Perguntas do intake respondidas

- **Qual e o delta real:** o template canonico separa `pending -> hold` e
  `pending -> approved`, enquanto F2/F3 agregam os dois caminhos em uma secao
  unica.
- **Quais ajustes minimos entram:** apenas o split do checklist e eventual
  normalizacao textual estritamente necessaria para explicitar veredito e estado
  do gate.
- **Como registrar a revalidacao sem parecer auditoria antecipada:** por
  evidencia comparativa no proprio fluxo `intake -> PRD -> planejamento/execucao
  futura`, sem relatorio de auditoria e sem nova linha no log.

### Cenarios obrigatorios

- **Drift confirmado:** F2 e F3 recebem apenas a separacao do checklist e
  mantem todo o restante intacto.
- **No-op controlado:** se um manifesto ja estiver aderente no momento da
  execucao, o resultado e somente evidenciado.
- **Nao-regressao:** nenhuma mudanca em `audit_gate`, `gate_atual`,
  `ultima_auditoria`, tabelas de epicos, dependencias, DoD ou `AUDIT-LOG.md`.
- **Validacao final documental:** comparacao linha a linha contra o template
  canonico e confirmacao de que F2/F3 continuam pre-auditoria.

---

## 9. Assuncoes

- o entregavel deste momento e apenas o rascunho do PRD
- a remediacao e minima e controlada, nao uma reabertura do FRAMEWORK2.0
- nao existe `DECISION-PROTOCOL.md` local exigindo rastreabilidade adicional
- a numeracao de artefatos futuros so sera decidida no momento de materializar
  planejamento ou execucao

---

## 10. Referencia de Intake

Este PRD deriva exclusivamente de
`INTAKE-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md`, com
contexto complementar de `RELATORIO-AUDITORIA-F1-R01.md`, `PRD-FRAMEWORK2.0.md`
e `AUDIT-LOG.md`, sem sobrescrever o PRD principal do projeto.