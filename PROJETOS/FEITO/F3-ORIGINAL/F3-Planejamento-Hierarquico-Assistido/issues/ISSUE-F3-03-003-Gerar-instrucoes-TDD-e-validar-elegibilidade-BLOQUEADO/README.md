---
doc_id: "ISSUE-F3-03-003-Gerar-instrucoes-TDD-e-validar-elegibilidade-BLOQUEADO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-03-003 - Gerar instrucoes TDD e validar elegibilidade BLOQUEADO

## User Story

Como PM do FRAMEWORK3, quero gerar instrucoes tdd e validar elegibilidade bloqueado para passo 15 do algoritmo coberto com instrucoes tdd e bloqueio de elegibilidade.

## Contexto Tecnico

As tasks required precisam carregar instrucoes operacionais suficientes e bloquear a execucao quando o recorte estiver incompleto. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Gerar instrucoes TDD e validar elegibilidade BLOQUEADO"
- Green: alinhamento minimo do recorte para entregar instrucoes tdd por task e retorno bloqueado aplicados no modulo
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Gerar instrucoes TDD e validar elegibilidade BLOQUEADO" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then instrucoes TDD por task e retorno BLOQUEADO aplicados no modulo.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Gerar instrucoes TDD para tasks automatizaveis](./TASK-1.md)
- [T2 - Bloquear execucao com task required incompleta](./TASK-2.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_tdd_instructions.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_blocked_eligibility.py`

## Artifact Minimo

Instrucoes TDD por task e retorno BLOQUEADO aplicados no modulo.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F3-03-Planejamento-de-Issues-Tasks-e-Instrucoes-TDD.md)
- [Fase](../../F3_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F3-03-002
