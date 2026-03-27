---
doc_id: "EPIC-F1-01-FUNDACAO-DO-PROJETO.md"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-23"
---

# EPIC-F1-01 - Fundacao do projeto

## Objetivo

Estabilizar o projeto-canario com docs coerentes, wrappers atuais e uma prova minima de execucao do framework.

## Resultado de Negocio Mensuravel

O framework passa primeiro pelo canario antes de atingir backlog real.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: canario de framework com guia, wrappers atuais e bootstrap operacional.

## Contexto Arquitetural

- guia de smoke como contrato do projeto
- wrappers locais apontando para a issue/bootstrap canario
- issue granularizada inicial para validar execucao, revisao e auditoria

## Definition of Done do Epico

- [ ] intake, PRD e guia do canario estao alinhados
- [ ] wrappers de sessao estao completos
- [ ] fase F1, epico, issue e task existem
- [ ] audit log aponta para o canario

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO | Estabilizar scaffold inicial do projeto-canario | Validar e ajustar o bootstrap do canario conforme o guia de smoke. | 3 | todo | [ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO) | Feature 1 |

## Artifact Minimo do Epico

- `README.md` da issue bootstrap
- `TASK-1.md`
- `F1_OC-SMOKE-SKILLS_EPICS.md`

## Dependencias

- [Intake](PROJETOS/OC-SMOKE-SKILLS/INTAKE-OC-SMOKE-SKILLS.md)
- [PRD](PROJETOS/OC-SMOKE-SKILLS/PRD-OC-SMOKE-SKILLS.md)
- [Guia](PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md)
- [Fase](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/F1_OC-SMOKE-SKILLS_EPICS.md)
