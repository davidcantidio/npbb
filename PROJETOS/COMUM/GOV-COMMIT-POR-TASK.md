---
doc_id: "GOV-COMMIT-POR-TASK.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
---

# GOV-COMMIT-POR-TASK

## Objetivo

Exigir commit apos cada task concluida para garantir rastreabilidade, checkpoint incremental e facilitar o fechamento correto de issues (status `done`). Evita que entregas fiquem sem evidencia em versionamento e que o agente omita a cascata de fechamento.

## Regra Obrigatoria

Apos concluir cada task (T1, T2, T3...) de uma issue, o executor deve fazer um commit com mensagem descritiva antes de prosseguir para a proxima task ou para o fechamento da issue.

## Formato da Mensagem de Commit

A mensagem deve conter, de forma legivel:

- **PROJETO**: nome do projeto (ex.: LP, FRAMEWORK2.0)
- **ISSUE_ID**: identificador da issue (ex.: ISSUE-F1-01-001)
- **TASK_ID**: identificador da task (ex.: T1, T2, T3)
- **Descricao breve**: o que foi feito na task (ex.: criar modelo Ativacao e migration)

### Formato canonico sugerido

```text
<PROJETO> <ISSUE_ID> <TASK_ID>: <descricao breve>
```

Exemplos:

```text
LP ISSUE-F1-01-001 T1: criar modelo Ativacao em models.py
LP ISSUE-F1-01-001 T2: criar migration Alembic para tabela ativacao
FRAMEWORK2.0 ISSUE-F2-03-001 T1: adicionar campo no schema
```

### Variantes aceitaveis

- `feat(LP): ISSUE-F1-01-001 T1 - criar modelo Ativacao`
- `[LP][ISSUE-F1-01-001][T1] criar modelo Ativacao`

O essencial e que PROJETO, ISSUE_ID e TASK_ID estejam presentes e identificaveis.

## Escopo de Aplicacao

- aplica-se a execucao de issues em modo autonomo (`boot-prompt.md`) e em modo sessao (`SESSION-IMPLEMENTAR-ISSUE.md`)
- aplica-se a issues com `task_instruction_mode: optional` e `required`
- quando a issue tem uma unica task (T1 apenas), o commit apos T1 e obrigatorio antes do fechamento
- quando a issue nao tem tasks decupadas explicitamente, o commit unico ao concluir a issue deve seguir o mesmo formato, usando T1 como TASK_ID

## Excecoes

- nenhuma: a regra e obrigatoria para toda execucao de issue que altere codigo ou documentos

## Referencias

- `GOV-SCRUM.md`: Procedimento de Fechamento de Issue (cascata apos todas as tasks)
- `SPEC-TASK-INSTRUCTIONS.md`: estrutura de tasks e instructions
- `SESSION-IMPLEMENTAR-ISSUE.md`: fluxo HITL com commit apos cada task
- `boot-prompt.md`: sequencia minima para ISSUE (modo autonomo)
