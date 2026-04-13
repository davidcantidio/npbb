---
doc_id: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-13"
audit_gate: "pending"
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
- audit_gate: `pending` (todas as user stories em `done`; aguarda `SESSION-AUDITAR-FEATURE` conforme `PROJETOS/COMUM/GOV-SCRUM.md`)
- proximo_passo_canonico: [`SESSION-AUDITAR-FEATURE`](../../../COMUM/SESSION-AUDITAR-FEATURE.md) sobre este manifesto de feature
- relatorio_mais_recente: [RELATORIO-AUDITORIA-F1-R01](auditorias/RELATORIO-AUDITORIA-F1-R01.md)
- audit_log: [AUDIT-LOG.md](../../AUDIT-LOG.md)

## Criterios de Aceite

- [x] existe um fluxo unico de lote Bronze com metadados de envio e arquivo
      bruto preservado
- [x] o operador consegue concluir a configuracao minima do estado Silver para o
      lote piloto
- [x] a primeira user story da feature chega a `done` com artefatos,
      caminhos e docs alinhados ao formato atual
- [x] a UI canonica de importacao reaproveita os contratos existentes e preserva
      compatibilidade para os deep links legados de mapeamento e pipeline
- [x] o projeto nao depende de wrappers ou backlog ativos do paradigma legado

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-1-01 | Ingestao e mapeamento inicial do lote | 5 | nenhuma | done | [README](./user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md) |
| US-1-02 | Tela unificada de importacao e estado do lote | 5 | US-1-01 | done | [README](./user-stories/US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE/README.md) |

## Definition of Done da Feature

- [x] todas as user stories estao `done` ou `cancelled`
- [ ] auditoria da feature aprovada com veredito `go`
- [ ] `AUDIT-LOG.md` atualizado com a rodada mais recente

## Backlog sugerido pos-auditoria (nao bloqueante)

- **Ramo ETL e `batch_id`:** a UI unificada nao persiste identificador de lote no fluxo ETL (ver limitacoes no handoff da US-1-02). **Nao** constitui reabertura da US-1-02. Avaliar nova US ou intake **somente** se o PRD ou o veredito de `SESSION-AUDITAR-FEATURE` exigirem retomada persistente e consulta de lote tambem para ETL.

## Dependencias

- [PRD](../../PRD-NPBB.md)
- [AUDIT-LOG](../../AUDIT-LOG.md)
- [User Story piloto](user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md)
