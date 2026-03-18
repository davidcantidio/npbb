---
doc_id: "F1_FW5_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
audit_gate: "not_ready"
---

# Epicos - FW5 / F1 - Fundacao do projeto

## Objetivo da Fase

Levar o PM do contexto bruto a um intake aprovado e a um PRD `feature-first` aprovado, com rastreabilidade e historico consultavel.

## Features Entregues

- Feature 1: Intake governado a partir de contexto bruto
- Feature 2: PRD `feature-first` derivado de intake aprovado

## Gate de Saida da Fase

Intake e PRD existem, foram revisados/aprovados e preservam rastreabilidade, restricoes, riscos, hipoteses declaradas e trilha de aprovacao.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/FW5/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- log_do_projeto: [PROJETOS/FW5/AUDIT-LOG.md](PROJETOS/FW5/AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F1-01 | Intake governado do projeto | Estruturar validar revisar e aprovar intake com historico de decisao. | Feature 1 | nenhuma | todo | [EPIC-F1-01-INTAKE-GOVERNADO-DO-PROJETO.md](./EPIC-F1-01-INTAKE-GOVERNADO-DO-PROJETO.md) |
| EPIC-F1-02 | PRD feature-first aprovado | Derivar revisar e aprovar PRD a partir do intake ja aprovado. | Feature 2 | EPIC-F1-01 | todo | [EPIC-F1-02-PRD-FEATURE-FIRST-APROVADO.md](./EPIC-F1-02-PRD-FEATURE-FIRST-APROVADO.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma
- `EPIC-F1-02`: EPIC-F1-01

## Escopo desta Fase

### Dentro
- intake estruturado com taxonomias, lacunas e gate `Intake -> PRD`
- revisao e aprovacao do intake com historico e diff
- PRD `feature-first` derivado do intake aprovado
- gate de aprovacao do PRD com rastreabilidade consultavel

### Fora
- derivacao de fases, epicos, issues e tasks do projeto
- selecao da proxima unidade elegivel e execucao assistida
- review pos-issue, auditoria operacional e timeline final

## Definition of Done da Fase
- [ ] intake pronto para PRD sem lacuna critica aberta
- [ ] PRD `feature-first` aprovado com criterios de aceite por feature
- [ ] historico de versoes e aprovacoes consultavel
- [ ] sprints F1 refletem o backlog canonico aprovado
