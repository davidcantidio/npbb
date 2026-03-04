---
doc_id: "PHASE-F4-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F4 UI Importacao Avancada - Epicos

## Objetivo da Fase

Expor o fluxo ETL avancado em `/leads`, com preview orientado por DQ report, commit governado por severidade e fechamento normativo auditavel da entrega.

## Gate de Saida da Fase

`make eval-integrations: PASS` e `make ci-quality: PASS`, a tab "Importacao avancada" esta funcional em `/leads`, e `artifacts/phase-f4/validation-summary.md` foi gerado com decisao `promote | hold`.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F4-01` | Tab Importacao Avancada | Adicionar uma tab dedicada ao fluxo ETL avancado em `/leads`, coexistindo com o fluxo legado. | `todo` | [EPIC-F4-01-TAB-IMPORTACAO-AVANCADA.md](./EPIC-F4-01-TAB-IMPORTACAO-AVANCADA.md) |
| `EPIC-F4-02` | DQ Report Widget | Exibir o `dq_report` antes do commit, com bloqueio por severidade e override explicito para warnings. | `todo` | [EPIC-F4-02-DQ-REPORT-WIDGET.md](./EPIC-F4-02-DQ-REPORT-WIDGET.md) |
| `EPIC-F4-03` | Coerencia Normativa e Gate | Consolidar os gates finais, cobertura cross-camada e evidencia auditavel da fase. | `todo` | [EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md](./EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md) |

## Escopo desta Entrega

Inclui a nova tab, service layer ETL, visualizacao do DQ report, governanca de commit por severidade e fechamento normativo da fase. Exclui novas mudancas de negocio fora do fluxo ETL avancado e alteracoes estruturais alem do necessario para concluir a UI.
