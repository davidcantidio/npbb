---
doc_id: "ISSUE-F2-01-002-Idempotencia-Dry-Run-Migracao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-01-002 - Idempotencia Dry-Run Migracao

## User Story

Como DevOps, quero que o script de migracao seja idempotente e possua dry-run, para executar com seguranca em producao e validar o impacto antes de aplicar.

## Contexto Tecnico

O script da ISSUE-F2-01-001 deve ser idempotente: executar multiplas vezes nao deve causar efeitos colaterais. O dry-run permite simular a execucao sem persistir. Parte disso pode ja estar na ISSUE-F2-01-001; esta issue garante que idempotencia e dry-run estejam completos e validados.

## Plano TDD

- Red: Teste que executa script duas vezes e verifica que estado final e identico
- Green: Script idempotente; dry-run nao persiste
- Refactor: Extrair validacoes comuns

## Criterios de Aceitacao

- Given o script executado com sucesso, When executo novamente, Then nenhuma alteracao adicional e feita (idempotencia)
- Given dry-run ativado, When executo o script, Then o banco permanece inalterado
- Given dry-run, When executo, Then o script reporta quantos registros seriam alterados

## Definition of Done da Issue
- [ ] Script idempotente validado
- [ ] Dry-run validado
- [ ] Teste automatizado cobrindo ambos os cenarios

## Tasks Decupadas

- [ ] T1: Garantir que o script so atualize registros que ainda contem localhost (condicao WHERE)
- [ ] T2: Validar dry-run com teste que verifica ausencia de alteracao no banco
- [ ] T3: Adicionar teste de idempotencia (executar 2x, verificar estado)

## Arquivos Reais Envolvidos

- Script de migracao da ISSUE-F2-01-001
- `backend/tests/` — testes do script

## Artifact Minimo

- Testes passando
- Documentacao atualizada

## Dependencias

- [Intake](../../INTAKE.md)
- [Epic](../EPIC-F2-01-Migracao.md)
- [Fase](../F2_QR-GEN_EPICS.md)
- [PRD](../../PRD-QR-GEN.md)
- [ISSUE-F2-01-001](./ISSUE-F2-01-001-Script-Migracao-Ativacao-Url.md) — script base
