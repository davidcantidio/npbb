---
doc_id: "GOV-COMMIT-POR-TASK.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# GOV-COMMIT-POR-TASK

## Objetivo

Exigir commit apos cada task concluida para garantir rastreabilidade,
checkpoint incremental e facilitar a transicao correta da issue para
`ready_for_review`, seguida do fechamento final apos revisao. Evita que
entregas fiquem sem evidencia em versionamento e que o agente omita o handoff
de revisao ou a sincronizacao documental minima.

## Regra Obrigatoria

Apos concluir cada task (T1, T2, T3...) de uma issue, o executor deve fazer um
commit com mensagem descritiva antes de prosseguir para a proxima task ou para
o handoff final da issue.

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

## Commit Final de Handoff de Revisao

Se, apos o ultimo commit de task, ainda houver alteracoes documentais para:

- persistir o handoff de revisao no manifesto da issue
- sincronizar a issue para `ready_for_review`
- refletir `ready_for_review` em epico, fase ou sprint

entao o executor deve fazer um commit final de fechamento documental.

Formato canonico sugerido:

```text
<PROJETO> <ISSUE_ID> CLOSE: preparar handoff de revisao
```

Exemplo:

```text
OC-MISSION-CONTROL ISSUE-F2-01-001 CLOSE: preparar handoff de revisao
```

## Escopo de Aplicacao

- aplica-se a execucao de user stories em modo autonomo (`boot-prompt.md`) e em modo sessao (`SESSION-IMPLEMENTAR-US.md`)
- aplica-se a issues com `task_instruction_mode: optional` e `required`
- quando a issue tem uma unica task (T1 apenas), o commit apos T1 e obrigatorio antes do fechamento
- quando a issue nao tem tasks decupadas explicitamente, o commit unico ao concluir a issue deve seguir o mesmo formato, usando T1 como TASK_ID
- se houver alteracoes documentais apos o ultimo commit de task, o commit final
  `CLOSE` tambem e obrigatorio antes de encerrar a execucao em `ready_for_review`

## Excecoes

- nenhuma: a regra e obrigatoria para toda execucao de issue que altere codigo ou documentos

## Referencias

- `GOV-SCRUM.md`: Procedimento de Review-Ready e Fechamento de Issue
- `SPEC-TASK-INSTRUCTIONS.md`: estrutura de tasks e instructions
- `SESSION-IMPLEMENTAR-US.md`: loop do agente local com commit apos cada task
- `boot-prompt.md`: sequencia minima para US (modo autonomo)
