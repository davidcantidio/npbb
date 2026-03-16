---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-01-008-Commit-e-Revalidar-Auditoria-F1"
task_id: "T2"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
---

# T2 - Revalidar auditoria com árvore limpa

## objetivo

Solicitar ou executar a revalidação da auditoria da F1 com árvore limpa e
commit SHA válido, para que o gate da fase possa ser aprovado (veredito `go`)
conforme GOV-AUDITORIA.

## precondicoes

- T1 concluída: árvore limpa e artefatos commitados
- `git status` confirma working tree clean
- commit SHA do HEAD disponível para o relatório de auditoria

## arquivos_a_ler_ou_tocar

- `PROJETOS/COMUM/GOV-AUDITORIA.md`
- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- `PROJETOS/SUPABASE/AUDIT-LOG.md`

## passos_atomicos

1. confirmar que a árvore está limpa (`git status`)
2. obter o commit SHA do HEAD para uso no relatório de revalidação
3. executar ou solicitar nova rodada de auditoria (F1-R02) conforme
   SESSION-AUDITAR-FASE, com base no commit atual
4. o relatório da nova rodada deve declarar que a árvore está limpa e que o
   follow-up B1 foi endereçado
5. se o veredito for `go`, o gate da fase será atualizado para `approved`

## comandos_permitidos

- `git status`
- `git rev-parse HEAD`
- comandos de auditoria conforme SESSION-AUDITAR-FASE (leitura de artefatos,
  execução de testes)

## resultado_esperado

Nova rodada de auditoria (F1-R02) executada com árvore limpa; veredito elegível
para aprovar o gate da fase; follow-up B1 declarado resolvido na prestação de
contas.

## testes_ou_validacoes_obrigatorias

- `RELATORIO-AUDITORIA-F1-R02.md` existe e referencia commit SHA válido
- seção "Prestação de Contas dos Follow-ups Anteriores" declara status do B1
- `AUDIT-LOG.md` atualizado com a nova rodada
- veredito `go` ou evidência de que o gate pode ser aprovado

## stop_conditions

- parar se a árvore não estiver limpa; retornar a T1
- parar se houver achado crítico ou high na revalidação que exija novo hold
- parar se o PM indicar que a revalidação será feita em sessão separada; neste
  caso, registrar o estado e aguardar
