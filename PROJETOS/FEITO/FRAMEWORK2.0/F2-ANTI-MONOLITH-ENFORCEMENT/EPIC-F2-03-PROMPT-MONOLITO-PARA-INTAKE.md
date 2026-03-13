---
doc_id: "EPIC-F2-03-PROMPT-MONOLITO-PARA-INTAKE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F2-03 - PROMPT-MONOLITO-PARA-INTAKE

## Objetivo

Transformar um achado estrutural em intake de remediacao com rastreabilidade
para a auditoria de origem.

## Resultado de Negocio Mensuravel

Ao encontrar um monolito acima de threshold, o auditor consegue abrir um intake
de refatoracao sem reescrever o contexto do zero.

## Contexto Arquitetural

- cria `PROMPT-MONOLITO-PARA-INTAKE.md`
- depende de `SPEC-ANTI-MONOLITO.md`
- depende de `TEMPLATE-INTAKE.md`

## Definition of Done do Epico

- [ ] prompt de monolito criado
- [ ] output esperado alinhado ao template de intake
- [ ] rastreabilidade para auditoria de origem obrigatoria

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-03-001 | Estruturar prompt monolito para intake | Definir input, validacoes e output do prompt. | 3 | todo | [ISSUE-F2-03-001-ESTRUTURAR-PROMPT-MONOLITO-PARA-INTAKE.md](./issues/ISSUE-F2-03-001-ESTRUTURAR-PROMPT-MONOLITO-PARA-INTAKE.md) |
| ISSUE-F2-03-002 | Validar prompt de monolito contra template de intake | Garantir que o prompt produz intake canonico. | 2 | todo | [ISSUE-F2-03-002-VALIDAR-PROMPT-DE-MONOLITO-CONTRA-TEMPLATE-DE-INTAKE.md](./issues/ISSUE-F2-03-002-VALIDAR-PROMPT-DE-MONOLITO-CONTRA-TEMPLATE-DE-INTAKE.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`

## Dependencias

- [Fase](./F2_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F2-01-SPEC-ANTI-MONOLITO.md)
