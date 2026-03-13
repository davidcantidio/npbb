---
doc_id: "EPIC-F3-05-SESSION-REFATORAR-MONOLITO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F3-05 - SESSION-REFATORAR-MONOLITO

## Objetivo

Criar o prompt de mini-projeto para decompor um arquivo ou funcao monolitica
com rastreabilidade desde o intake ate a auditoria final.

## Resultado de Negocio Mensuravel

Quando a auditoria abrir uma remediacao estrutural, o PM consegue percorrer o
fluxo completo em chat sem montar manualmente cada etapa.

## Contexto Arquitetural

- cria `SESSION-REFATORAR-MONOLITO.md`
- depende de `PROMPT-MONOLITO-PARA-INTAKE.md`
- encadeia sessoes de PRD, planejamento, implementacao e auditoria

## Definition of Done do Epico

- [ ] sessao de refatoracao criada
- [ ] fluxo completo de mini-projeto documentado
- [ ] validacao de compatibilidade de interface incluida

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-05-001 | Redigir SESSION-REFATORAR-MONOLITO como mini projeto guiado | Criar o fluxo de alto nivel da remediacao. | 3 | todo | [ISSUE-F3-05-001-REDIGIR-SESSION-REFATORAR-MONOLITO-COMO-MINI-PROJETO.md](./issues/ISSUE-F3-05-001-REDIGIR-SESSION-REFATORAR-MONOLITO-COMO-MINI-PROJETO.md) |
| ISSUE-F3-05-002 | Validar encadeamento intake PRD fases issues e auditoria de compatibilidade | Garantir que a sessao fecha o fluxo completo sem lacunas. | 2 | todo | [ISSUE-F3-05-002-VALIDAR-ENCADEAMENTO-INTAKE-PRD-E-AUDITORIA-DE-COMPATIBILIDADE.md](./issues/ISSUE-F3-05-002-VALIDAR-ENCADEAMENTO-INTAKE-PRD-E-AUDITORIA-DE-COMPATIBILIDADE.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`

## Dependencias

- [Fase](./F3_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md)
- [F2](../F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md)
