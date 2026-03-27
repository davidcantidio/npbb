---
doc_id: "RELATORIO-AUDITORIA-F1-R01.md"
version: "2.2"
status: "planned"
scope_type: "phase"
scope_ref: "F1-FUNDACAO"
phase: "F1"
reviewer_model: "nao_aplicavel"
base_commit: "HEAD"
compares_to: "none"
round: 1
supersedes: "none"
followup_destination: "issue-local"
decision_refs: []
last_updated: "2026-03-25"
---

# RELATORIO-AUDITORIA - TESTE-FW / F1-FUNDACAO / R01

## Resumo Executivo

Este ficheiro e um **template/shell** para a primeira rodada de auditoria da fase. Com `status: planned`, a rodada **nao foi executada** (`GOV-AUDITORIA.md`). O `AUDIT-LOG.md` do projeto mantem `Ultima Auditoria: nao_aplicavel` e a tabela **Rodadas** vazia ate haver execucao real e registo alinhado.

## Escopo Auditado e Evidencias

- intake: [INTAKE-TESTE-FW.md](../../INTAKE-TESTE-FW.md)
- prd: [PRD-TESTE-FW.md](../../PRD-TESTE-FW.md)
- fase: [Fase](../F1_TESTE-FW_EPICS.md)
- epicos: [Epic bootstrap](../EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- issues: [Issue bootstrap](../issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md)
- testes: `tests/test_criar_projeto.py`
- diff/commit: nao aplicavel ainda

## Conformidades

- nao aplicavel enquanto `planned` — placeholders de links para a futura rodada

## Nao Conformidades

- nao aplicavel — shell; achados materiais apenas apos auditoria executada

## Verificacao de Decisoes Registradas

| Decision Ref | Resultado | Evidencia | Observacoes |
|---|---|---|---|
| nenhum | nao aplicavel | shell `planned` | preencher na rodada real |

## Analise de Complexidade Estrutural

| ID | Componente | Tipo | Linguagem | Metricas observadas | Threshold de referencia | Tendencia vs rodada anterior | Bloqueante? | Destino sugerido |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | nao aplicavel ao shell | — | — | — | — |

## Bugs e Riscos Antecipados

| ID | Categoria | Severidade | Descricao | Evidencia | Correcao sugerida | Bloqueante? |
|---|---|---|---|---|---|---|
| — | — | — | nao aplicavel ao shell | — | — | — |

## Cobertura de Testes

| Funcionalidade | Teste existe? | Tipo | Observacao |
|---|---|---|---|
| scaffold do projeto | sim | unit | cobre tree, wrappers e doc_ids; avaliacao de auditoria na rodada real |

## Decisao

- estado do artefato: `planned` (rodada nao executada; ver `GOV-AUDITORIA.md`)
- veredito canonico (`go` / `hold` / `cancelled`): **nao aplicavel** ate conclusao da rodada e atualizacao deste relatorio para `done` (ou estado em curso definido em GOV), com entrada correspondente em `AUDIT-LOG.md` na tabela **Rodadas**
- gate_da_fase no manifesto da fase: continua governado pelo Markdown da fase e pelo log; este shell nao altera o gate
- follow-ups materiais e `followup_destination`: apenas apos veredito real

## Handoff para Novo Intake

> Preencher apenas quando houver remediacao estrutural ou sistemica com destino `new-intake`.

- nome_sugerido_do_intake: nao aplicavel
- intake_kind_recomendado: nao aplicavel
- problema_resumido: scaffold base apenas
- evidencias: nao aplicavel
- impacto: nao aplicavel
- escopo_presumido: nao aplicavel

## Follow-ups Bloqueantes

1. nao aplicavel ao shell `planned`

## Follow-ups Nao Bloqueantes

1. nao aplicavel ao shell `planned`
