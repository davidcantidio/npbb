---
doc_id: "ISSUE-F1-01-008-Commit-e-Revalidar-Auditoria-F1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-008 - Commit e revalidar auditoria F1

## User Story

Como revisor da F1, quero fazer commit dos artefatos pendentes e revalidar a
auditoria com árvore limpa, para que o gate da fase possa ser aprovado conforme
GOV-AUDITORIA.

## Contexto Tecnico

Esta issue nasce do follow-up B1 da auditoria F1-R01 (hold).

Rastreabilidade obrigatória:
- relatório de origem: [RELATORIO-AUDITORIA-F1-R01.md](../../auditorias/RELATORIO-AUDITORIA-F1-R01.md)
- evidência: worktree sujo na data da auditoria; GOV-AUDITORIA exige commit SHA
  e árvore limpa para aprovar gate
- sintoma observado: auditoria F1-R01 marcada como `provisional` por worktree
  sujo; veredito `hold` com follow-up bloqueante
- risco de não corrigir: a F1 permanece em `hold` e não pode avançar para
  `feito/`; a F2 depende do gate aprovado da F1

Escopo desta correção:
- fazer commit dos artefatos da F1 (arquivos modificados e não rastreados)
- garantir árvore limpa
- solicitar revalidação da auditoria com árvore limpa para aprovar gate
- não alterar código funcional; apenas consolidar artefatos documentais e de
  código já produzidos

## Plano TDD

- Red: evidenciar por `git status` que a árvore está suja
- Green: commit dos artefatos e revalidação da auditoria com árvore limpa
- Refactor: manter a remediação mínima; nenhuma alteração funcional

## Criterios de Aceitacao

- Given o worktree estava sujo na auditoria F1-R01, When esta issue for
  concluída, Then todos os artefatos relevantes da F1 estão commitados
- Given GOV-AUDITORIA exige árvore limpa, When a revalidação for solicitada,
  Then `git status` mostra working tree clean
- Given o follow-up B1 é bloqueante, When esta issue estiver `done`, Then a
  próxima rodada de auditoria pode ser iniciada
- Given esta issue é de remediação pós-hold, When ela for executada, Then a
  rastreabilidade ao relatório F1-R01 permanece explícita

## Definition of Done da Issue

- [x] todos os artefatos da F1 estão commitados
- [x] árvore limpa (`git status` sem arquivos M ou ??)
- [x] revalidação da auditoria solicitada ou executada com árvore limpa
- [x] dependência ao relatório F1-R01 documentada nesta issue

## Tasks

- [T1: Fazer commit dos artefatos da F1](./TASK-1.md)
- [T2: Revalidar auditoria com árvore limpa](./TASK-2.md)

## Arquivos Reais Envolvidos

- artefatos modificados/não rastreados identificados por `git status` no momento
  da execução
- `PROJETOS/SUPABASE/AUDIT-LOG.md` (atualização na revalidação)
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/auditorias/RELATORIO-AUDITORIA-F1-R01.md`

## Artifact Minimo

- commits com artefatos da F1 consolidados
- árvore limpa
- revalidação da auditoria F1 com veredito elegível para aprovar gate

## Dependencias

- [Intake](../../../INTAKE-SUPABASE.md)
- [Epic](../../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../../F1_SUPABASE_EPICS.md)
- [PRD](../../../PRD-SUPABASE.md)
- [RELATORIO-AUDITORIA-F1-R01](../../auditorias/RELATORIO-AUDITORIA-F1-R01.md) (follow-up B1)
