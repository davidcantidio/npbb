---
doc_id: "RELATORIO-AUDITORIA-F<N>-R<NN>.md"
version: "1.0"
status: "planned"
verdict: "hold"
feature_id: "F<N>"
reviewer_model: "<MODEL>"
base_commit: "<sha>"
round: 1
supersedes: "none"
followup_destination: "issue-local"
last_updated: "YYYY-MM-DD"
---

# RELATORIO-AUDITORIA - <PROJETO> / FEATURE <F<N>> / R<NN>

## Resumo Executivo

> Preencher em no maximo 3 linhas, resumindo escopo auditado, principal risco e
> recomendacao de gate.

## Escopo Auditado

- intake:
- prd:
- feature:
- user_stories:
- testes:
- diff/commit:
- evidencias_relevantes:

## Prestacao de Contas de Follow-ups

> Preencher apenas quando `round > 1` e a rodada imediatamente anterior tiver
> veredito `hold`. Omitir completamente em rodada inicial ou quando a rodada
> anterior nao for `hold`.
>
> Usar `feature_id`, `round`, `supersedes` e o `AUDIT-LOG.md` para localizar a
> rodada de referencia. Listar apenas os follow-ups da rodada `hold`
> imediatamente anterior. Nao incluir follow-ups de rodadas mais antigas.

| Follow-up | Tipo | Destino Final | Status verificado | Arquivo ou registro | Observacoes |
|---|---|---|---|---|---|
| B1 | bloqueante | issue-local | done | `README.md` da US corretiva ou `AUDIT-LOG.md` | encerrado |
| N1 | nao bloqueante | new-intake | criado | `INTAKE-*.md` | nao bloqueia |
| C1 | bloqueante | cancelled | registrado no log | `AUDIT-LOG.md` | justificativa registrada |

Resultado da prestacao de contas: `completa` / `parcial - ver observacoes`

> `parcial` nao impede veredito `go`, mas exige justificativa explicita de por
> que o item pendente nao bloqueia o gate desta rodada.

## Conformidades

- 
- 

## Nao Conformidades

> Cada achado deve trazer evidencia objetiva. Consolidar aqui bugs, riscos,
> `test-gap` e aderencia ou desvio de decisoes registradas, quando houver.

| ID | Categoria | Severidade | Descricao | Evidencia | Correcao sugerida | Bloqueante? |
|---|---|---|---|---|---|---|
| A-01 | bug | high |  |  |  | sim |
| A-02 | test-gap | medium |  |  |  | nao |
| A-03 | architecture-drift | medium |  |  |  | nao |

## Analise Estrutural

> Usar `SPEC-ANTI-MONOLITO.md` como fonte unica de thresholds para
> `monolithic-file` e `monolithic-function`.

| ID | Componente | Tipo | Linguagem | Metricas observadas | Threshold de referencia | Tendencia vs rodada anterior | Bloqueante? | Destino sugerido |
|---|---|---|---|---|---|---|---|---|
| M-01 |  | monolithic-file |  |  |  |  | nao | issue-local |

## Decisao

- veredito:
- justificativa:
- gate_da_feature:
- follow_up_destino_padrao:

## Follow-ups

### Follow-ups Bloqueantes

1. 

### Follow-ups Nao Bloqueantes

1. 

### Handoff para Novo Intake

> Preencher apenas quando houver remediacao estrutural ou sistemica com destino
> `new-intake`.

- nome_sugerido_do_intake:
- intake_kind_recomendado:
- problema_resumido:
- evidencias:
- impacto:
- escopo_presumido:
