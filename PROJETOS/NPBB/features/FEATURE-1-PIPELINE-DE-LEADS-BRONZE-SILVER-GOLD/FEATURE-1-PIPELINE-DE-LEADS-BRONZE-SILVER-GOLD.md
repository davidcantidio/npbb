---
doc_id: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
audit_gate: "not_ready"
---

# FEATURE-1 - Pipeline de Leads Bronze Silver Gold

## Objetivo de Negocio

Entregar o primeiro piloto real do framework atual no `npbb`, unificando a
ingestao de leads em um fluxo Bronze -> Silver -> Gold com rastreabilidade do
arquivo bruto ate o estado promovido.

## Resultado de Negocio Mensuravel

O operador consegue importar um lote, concluir o mapeamento inicial e iniciar o
pipeline Gold sem sair do fluxo governado atual do projeto.

## Dependencias da Feature

- nenhuma

## Estado Operacional

- status: `active`
- audit_gate: `not_ready`
- relatorio_mais_recente: [RELATORIO-AUDITORIA-F1-R01](auditorias/RELATORIO-AUDITORIA-F1-R01.md)
- audit_log: [AUDIT-LOG.md](../../AUDIT-LOG.md)

## Criterios de Aceite

- [ ] existe um fluxo unico de lote Bronze com metadados de envio e arquivo
      bruto preservado
- [ ] o operador consegue concluir a configuracao minima do estado Silver para o
      lote piloto
- [ ] a primeira user story da feature chega a `ready_for_review` com artefatos,
      caminhos e docs alinhados ao formato atual
- [ ] o projeto nao depende de wrappers ou backlog ativos do paradigma legado

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-1-01 | Ingestao e mapeamento inicial do lote | 5 | nenhuma | todo | [README](./user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md) |

## Definition of Done da Feature

- [ ] todas as user stories estao `done` ou `cancelled`
- [ ] auditoria da feature aprovada com veredito `go`
- [ ] `AUDIT-LOG.md` atualizado com a rodada mais recente

## Dependencias

- [PRD](../../PRD-NPBB.md)
- [AUDIT-LOG](../../AUDIT-LOG.md)
- [User Story piloto](user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md)
