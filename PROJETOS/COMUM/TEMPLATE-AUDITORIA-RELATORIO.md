---
doc_id: "RELATORIO-AUDITORIA-F<N>-R<NN>.md"
version: "2.1"
status: "planned"
verdict: "hold"
scope_type: "phase"
scope_ref: "F<N>-<NOME>"
phase: "F<N>"
reviewer_model: "<MODEL>"
base_commit: "<sha>"
compares_to: "<audit_id-anterior-ou-none>"
round: 1
supersedes: "none"
followup_destination: "issue-local"
decision_refs:
  - "<decision-id-ou-none>"
last_updated: "YYYY-MM-DD"
---

# RELATORIO-AUDITORIA - <PROJETO> / <FASE> / R<NN>

## Resumo Executivo

## Escopo Auditado e Evidencias

- intake:
- prd:
- fase:
- epicos:
- issues:
- testes:
- diff/commit:

## Prestacao de Contas dos Follow-ups Anteriores

> Preencher apenas quando `round > 1` e a rodada imediatamente anterior
> referenciada em `compares_to` tiver veredito `hold`. Omitir completamente em
> rodadas iniciais ou quando a rodada anterior for `go`.
>
> Listar apenas os follow-ups da rodada hold imediatamente anterior (identificada
> em `compares_to`). Nao incluir follow-ups de rodadas mais antigas.

| Follow-up | Tipo | Destino Final | Status verificado | Arquivo ou registro | Observacoes |
|---|---|---|---|---|---|
| B1 | bloqueante | issue-local | done | [ISSUE-*.md](./issues/ISSUE-*.md) | encerrado |
| N1 | nao bloqueante | new-intake | criado | [INTAKE-*.md](../../INTAKE-*.md) | nao bloqueia |
| C1 | bloqueante | cancelled | registrado no log | `AUDIT-LOG.md` | justificativa registrada |

Resultado da prestacao de contas: `completa` / `parcial — ver observacoes`

> `parcial` nao impede o veredito `go`, mas exige justificativa explicita de por
> que o follow-up pendente nao bloqueia o gate desta rodada.

## Conformidades

- 
- 

## Nao Conformidades

- 
- 

## Verificacao de Decisoes Registradas

| Decision Ref | Resultado | Evidencia | Observacoes |
|---|---|---|---|
| `dec-...` | aderente |  |  |

## Analise de Complexidade Estrutural

> Usar `SPEC-ANTI-MONOLITO.md` como fonte de threshold.

| ID | Componente | Tipo | Linguagem | Metricas observadas | Threshold de referencia | Tendencia vs rodada anterior | Bloqueante? | Destino sugerido |
|---|---|---|---|---|---|---|---|---|
| M-01 |  | monolithic-file |  |  |  |  | nao | issue-local |

## Bugs e Riscos Antecipados

| ID | Categoria | Severidade | Descricao | Evidencia | Correcao sugerida | Bloqueante? |
|---|---|---|---|---|---|---|
| A-01 | bug | high |  |  |  | sim |

## Cobertura de Testes

| Funcionalidade | Teste existe? | Tipo | Observacao |
|---|---|---|---|
|  |  |  |  |

## Decisao

- veredito:
- justificativa:
- gate_da_fase:
- follow_up_destino_padrao:

## Handoff para Novo Intake

> Preencher apenas quando houver remediacao estrutural ou sistemica com destino `new-intake`.

- nome_sugerido_do_intake:
- intake_kind_recomendado:
- problema_resumido:
- evidencias:
- impacto:
- escopo_presumido:

## Follow-ups Bloqueantes

1. 

## Follow-ups Nao Bloqueantes

1. 
