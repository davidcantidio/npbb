---
doc_id: "EPIC-F3-04-SESSION-AUDITAR-FASE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F3-04 - SESSION-AUDITAR-FASE

## Objetivo

Criar o prompt de auditoria interativa com proposta de veredito, update de
audit log e opcao inline de remediacao estrutural.

## Resultado de Negocio Mensuravel

O PM consegue conduzir uma auditoria de fase em chat sem improvisar checklist
ou fluxo de follow-up.

## Contexto Arquitetural

- cria `SESSION-AUDITAR-FASE.md`
- depende de `TEMPLATE-AUDITORIA-RELATORIO.md`, `SPEC-ANTI-MONOLITO.md` e `PROMPT-MONOLITO-PARA-INTAKE.md`

## Definition of Done do Epico

- [ ] sessao de auditoria criada
- [ ] monolito acima de threshold aciona caminho de remediacao
- [ ] gravacao de relatorio e audit log exige confirmacao

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-04-001 | Redigir SESSION-AUDITAR-FASE com fluxo HITL | Criar o fluxo base da sessao de auditoria. | 3 | todo | [ISSUE-F3-04-001-REDIGIR-SESSION-AUDITAR-FASE-COM-FLUXO-HITL.md](./issues/ISSUE-F3-04-001-REDIGIR-SESSION-AUDITAR-FASE-COM-FLUXO-HITL.md) |
| ISSUE-F3-04-002 | Integrar remediacao anti monolito e atualizacao de audit log | Completar o caminho de follow-up estrutural e escrita controlada. | 2 | todo | [ISSUE-F3-04-002-INTEGRAR-REMEDIACAO-ANTI-MONOLITO-E-AUDIT-LOG.md](./issues/ISSUE-F3-04-002-INTEGRAR-REMEDIACAO-ANTI-MONOLITO-E-AUDIT-LOG.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`

## Dependencias

- [Fase](./F3_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md)
- [F2](../F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md)
