---
doc_id: "ISSUE-F1-02-001-DEPRECAR-O-LEGADO-DUPLICADO-E-LIMPAR-RASTROS-DE-REFERENCIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-02-001 - Deprecar o legado duplicado e limpar rastros de referencia

## User Story

Como mantenedor do framework, quero retirar o legado duplicado do caminho de leitura
para reduzir a chance de um agente usar a fonte normativa errada.

## Contexto Tecnico

O PRD confirmou a existencia de `PROJETOS/scrum-framework-master (1).md`. A issue
fecha a deprecacao formal desse artefato apos a renomeacao comum.

## Plano TDD

- Red: confirmar a existencia e o papel do legado.
- Green: remover o legado e revisar rastros obrigatorios.
- Refactor: revisar a nota de deprecacao para nao conflitar com o framework novo.

## Criterios de Aceitacao

- Given o legado duplicado, When a issue for concluida, Then ele nao aparece mais como fonte canonica ativa
- Given a revisao de referencias, When a busca terminar, Then nenhum entrypoint obrigatorio aponta para o legado

## Definition of Done da Issue

- [x] legado retirado do caminho canonico
- [x] rastros obrigatorios revisados

## Tasks Decupadas

- [x] T1: confirmar o arquivo legado e seu contexto
- [x] T2: retirar o legado do caminho canonico
- [x] T3: revisar referencias obrigatorias restantes

## Arquivos Reais Envolvidos

- `PROJETOS/scrum-framework-master (1).md`
- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`

## Artifact Minimo

- `PROJETOS/scrum-framework-master (1).md`

## Dependencias

- [Epic Dependente](../EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
- [Epic](../EPIC-F1-02-DEPRECACAO-DO-LEGADO.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
