---
doc_id: "GOV-COMMIT-POR-TASK.md"
version: "1.3"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# GOV-COMMIT-POR-TASK

## Objetivo

Exigir commit apos cada task concluida para garantir rastreabilidade,
checkpoint incremental e facilitar a transicao correta da user story para
`ready_for_review`, seguida do fechamento final apos revisao. Evita que
entregas fiquem sem evidencia em versionamento e que o agente omita o handoff
de revisao ou a sincronizacao documental minima.

## Regra Obrigatoria

Apos concluir cada task (T1, T2, T3...) de uma user story, o executor deve fazer um
commit com mensagem descritiva antes de prosseguir para a proxima task ou para
o handoff final da user story.

## Formato da Mensagem de Commit

A mensagem deve conter, de forma legivel:

- **PROJETO**: nome do projeto (ex.: LP, FRAMEWORK2.0)
- **US_ID**: identificador da user story (ex.: US-1-01)
- **TASK_ID**: identificador da task (ex.: T1, T2, T3)
- **Descricao breve**: o que foi feito na task (ex.: criar modelo Ativacao e migration)

### Formato canonico sugerido

```text
<PROJETO> <US_ID> <TASK_ID>: <descricao breve>
```

Exemplos:

```text
LP US-1-01 T1: criar modelo Ativacao em models.py
LP US-1-01 T2: criar migration Alembic para tabela ativacao
FRAMEWORK2.0 US-2-03 T1: adicionar campo no schema
```

### Variantes aceitaveis

- `feat(LP): US-1-01 T1 - criar modelo Ativacao`
- `[LP][US-1-01][T1] criar modelo Ativacao`

O essencial e que PROJETO, US_ID e TASK_ID estejam presentes e identificaveis.

Referencias legadas a `ISSUE_ID` podem ser lidas como compatibilidade documental
ao operar artefatos antigos, mas nao definem o contrato novo.

## Commit Final de Handoff de Revisao

Se, apos o ultimo commit de task, ainda houver alteracoes documentais para:

- persistir o handoff de revisao no manifesto da user story
- sincronizar a user story para `ready_for_review`
- refletir `ready_for_review` na feature pai

entao o executor deve fazer um commit final de fechamento documental.

Formato canonico sugerido:

```text
<PROJETO> <US_ID> CLOSE: preparar handoff de revisao
```

Exemplo:

```text
OC-MISSION-CONTROL US-2-01 CLOSE: preparar handoff de revisao
```

## Gate automatico antes de `ready_for_review`

Antes de promover a user story para `ready_for_review`, o executor deve validar
o par `TASK done` + commit por task + handoff:

```bash
python3 scripts/framework_governance/validate_us_traceability.py \
  --repo-root . \
  --us-path PROJETOS/<PROJETO>/features/FEATURE-<N>-<NOME>/user-stories/US-<N>-<NN>-<NOME> \
  --json
```

Se o validador falhar, a user story nao esta apta para `ready_for_review`.

O CI do repositorio (`/.github/workflows/ci.yml`) corre tambem um varrimento
agregado sobre todas as user stories com `status: ready_for_review`:

```bash
python3 scripts/framework_governance/scan_us_traceability.py --repo-root .
```

- Se **nenhuma** US estiver nesse estado, o passo termina logo (exit `0`).
- Para desligar o passo num clone ou job experimental:
  `OPENCLAW_SKIP_US_TRACEABILITY_SCAN=1`.

## Escopo de Aplicacao

- aplica-se a execucao de user stories em modo autonomo (`boot-prompt.md`) e em modo sessao (`SESSION-IMPLEMENTAR-US.md`)
- aplica-se a user stories com `task_instruction_mode: optional` e `required`
- quando a user story tem uma unica task (T1 apenas), o commit apos T1 e obrigatorio antes do fechamento
- quando a user story nao tem tasks decupadas explicitamente, o commit unico ao concluir a user story deve seguir o mesmo formato, usando T1 como TASK_ID
- se houver alteracoes documentais apos o ultimo commit de task, o commit final
  `CLOSE` tambem e obrigatorio antes de encerrar a execucao em `ready_for_review`

## Excecoes

- nenhuma: a regra e obrigatoria para toda execucao de user story que altere codigo ou documentos

## Referencias

- `GOV-SCRUM.md`: Procedimento de Review-Ready e Fechamento de User Story
- `SPEC-TASK-INSTRUCTIONS.md`: estrutura de tasks e instructions
- `SESSION-IMPLEMENTAR-US.md`: loop do agente local com commit apos cada task
- `boot-prompt.md`: sequencia minima para US (modo autonomo)
- `scripts/framework_governance/validate_us_traceability.py`: gate automatico de task/commit/handoff
- `scripts/framework_governance/scan_us_traceability.py`: varrimento CI sobre US em `ready_for_review`
