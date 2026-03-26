---
doc_id: "FEATURE-1.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
audit_gate: "not_ready"
---

# FEATURE-1 - Foundation

## Objetivo de Negocio

Entregar o scaffold inicial do projeto no paradigma
`Feature -> User Story -> Task`, com wrappers locais e auditabilidade
prontos para uso.

## Resultado de Negocio Mensuravel

O PM consegue iniciar planejamento e execucao sem preencher manualmente
os cabecalhos principais nem adaptar caminhos legados.

## Dependencias da Feature

- nenhuma

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`
- relatorio_mais_recente: [RELATORIO-AUDITORIA-F1-R01](auditorias/RELATORIO-AUDITORIA-F1-R01.md)
- audit_log: [AUDIT-LOG.md](../../AUDIT-LOG.md)

## Criterios de Aceite

- [ ] intake, PRD e audit log existem com frontmatter preenchido
- [ ] wrappers locais apontam para `SESSION-IMPLEMENTAR-US`,
      `SESSION-REVISAR-US` e `SESSION-AUDITAR-FEATURE`
- [ ] `features/FEATURE-1-FOUNDATION/` existe com manifesto, user story
      bootstrap e `TASK-1.md`
- [ ] nao existem `F1-*`, `issues/`, `sprints/` nem wrappers
      `SESSION-*-ISSUE/FASE` no projeto novo

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-1-01 | Bootstrap do projeto | 3 | nenhuma | todo | [README](./user-stories/US-1-01-BOOTSTRAP/README.md) |

## Definition of Done da Feature

- [ ] todas as user stories estao `done` ou `cancelled`
- [ ] auditoria da feature aprovada com veredito `go`
- [ ] `AUDIT-LOG.md` atualizado com a rodada mais recente

## Dependencias

- [PRD](../../PRD-DASHBOARD-ATIVOS.md)
- [AUDIT-LOG](../../AUDIT-LOG.md)
- [User Story bootstrap](user-stories/US-1-01-BOOTSTRAP/README.md)
