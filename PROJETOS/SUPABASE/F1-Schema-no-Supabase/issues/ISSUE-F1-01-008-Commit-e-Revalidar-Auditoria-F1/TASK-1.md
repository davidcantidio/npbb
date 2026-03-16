---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-008-Commit-e-Revalidar-Auditoria-F1"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
---

# T1 - Fazer commit dos artefatos da F1

## objetivo

Consolidar em commits os artefatos modificados e não rastreados da F1, de forma
que a árvore fique limpa e elegível para revalidação da auditoria conforme
GOV-AUDITORIA.

## precondicoes

- relatório F1-R01 lido; follow-up B1 compreendido
- `git status` executado para identificar arquivos M e ??
- decisão sobre agrupamento de commits (um por tipo de artefato ou um único
  commit de consolidação) tomada conforme GOV-COMMIT-POR-TASK

## arquivos_a_ler_ou_tocar

- arquivos listados por `git status` no momento da execução
- `PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md`
- `PROJETOS/COMUM/GOV-AUDITORIA.md`

## passos_atomicos

1. executar `git status` e listar arquivos modificados (M) e não rastreados (??)
2. agrupar artefatos por coerência (ex.: documentação PROJETOS/, código backend/)
3. para cada grupo ou artefato, executar `git add` e `git commit` com mensagem
   descritiva conforme GOV-COMMIT-POR-TASK (PROJETO, ISSUE_ID, TASK_ID, descrição)
4. repetir até `git status` mostrar working tree clean
5. não alterar conteúdo funcional; apenas versionar o que já existe

## comandos_permitidos

- `git status`
- `git add <path>`
- `git commit -m "<mensagem>"`
- `git diff` (leitura)

## resultado_esperado

Árvore limpa; todos os artefatos da F1 relevantes commitados.

## testes_ou_validacoes_obrigatorias

- `git status` retorna "nothing to commit, working tree clean"
- nenhum arquivo M ou ?? restante

## stop_conditions

- parar se houver conflito de merge ou rebase em andamento
- parar se a decisão de commit exigir alterar código funcional além do que já
  existe no worktree
