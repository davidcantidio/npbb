---
doc_id: "SPEC-TASK-INSTRUCTIONS.md"
version: "2.2"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SPEC-TASK-INSTRUCTIONS

## Objetivo

Definir como `instructions` atomicas devem viver dentro de `tasks` no padrao `issue-first`, sem criar novo artefato raiz para execucao.

## Conceitos

- `issue`: unidade documental completa de execucao
- `task`: menor unidade executavel dentro da issue
- `instruction`: menor unidade atomica de execucao dentro da task

Regra canonica:

- `instruction` nunca vira arquivo independente
- `instruction` vive inline na issue, na secao `## Instructions por Task`, ou no corpo de
  `TASK-N.md` quando a issue for granularizada
- `task` pode ser checklist curto (issue legada) ou arquivo `TASK-N.md` (issue granularizada);
  `instruction` operacionaliza o como executar

## Campo Canonico da Issue

Toda issue nova ou revisada deve declarar no frontmatter:

```yaml
task_instruction_mode: "optional"
```

Valores aceitos:

- `optional`
- `required`

## Quando `required` e obrigatorio

Use `task_instruction_mode: required` quando a issue contiver qualquer um destes fatores:

- migration ou mudanca com persistencia/rollback sensivel
- ordem de execucao critica
- alteracao multi-camada ou multi-arquivo com dependencia forte
- remediacao originada de auditoria `hold`
- remediacao originada de revisao pos-issue com risco alto ou regressao delicada
- handoff planejado para outra IA ou sessao

Se nenhum desses fatores existir, `optional` e o default recomendado.

## Estrutura Minima do Detalhamento por Task

Quando `task_instruction_mode: required`, a issue precisa ter:

- tasks identificadas de forma rastreavel (`T1`, `T2`, `T3`...)
- um detalhamento vinculante por task no formato escolhido:
  - issue granularizada: um arquivo `TASK-N.md` por task
  - issue legada: secao `## Instructions por Task` com um bloco por task

Campos minimos por task:

- `objetivo`
- `precondicoes`
- `arquivos_a_ler_ou_tocar`
- `passos_atomicos`
- `comandos_permitidos`
- `resultado_esperado`
- `testes_ou_validacoes_obrigatorias`
- `stop_conditions`

## Criterio de Atomicidade

Uma instruction atomica deve:

- descrever uma unica acao verificavel por passo
- evitar branching pesado ou fluxos com muitas alternativas
- explicitar ordem quando a sequencia for critica
- permitir que outro agente execute sem reinterpretar o objetivo da task
- dizer claramente quando parar e reportar bloqueio

Uma instruction ruim costuma:

- misturar varias alteracoes em um unico passo
- depender de conhecimento tacito nao documentado
- omitir arquivos ou testes obrigatorios
- usar formulacoes vagas como "ajustar se necessario" sem criterio objetivo

## Regra de Elegibilidade

- issue com `task_instruction_mode: required` sem detalhamento completo por task no formato escolhido nao e elegivel para execucao
- o agente executor deve responder `BLOQUEADO` em vez de improvisar
- o bloqueio vale tambem quando houver task sem `TASK-N.md` correspondente, sem bloco correspondente em `## Instructions por Task`, ou com campos minimos ausentes

## Compatibilidade de Rollout

- issues antigas sem `task_instruction_mode` podem ser tratadas como `optional` ate serem revisadas
- nao ha retrofit em massa obrigatorio neste rollout
- qualquer issue nova de alto risco deve nascer com `task_instruction_mode: required`

## Issue Granularizada (Pasta com TASK-N.md)

Quando a issue for uma pasta `issues/ISSUE-*/` com `README.md` e `TASK-*.md`:

- cada task vive em arquivo proprio `TASK-N.md`; usar `TEMPLATE-TASK.md` como base
- o `README.md` contem o manifesto (User Story, Contexto, DoD, Dependencias) e lista de links
  para as tasks
- issues legadas (arquivo unico `ISSUE-*.md`) continuam validas; o executor detecta o formato
  e aplica o fluxo correto

## Exemplo Canonico - Issue Granularizada Required

```markdown
issues/ISSUE-F1-01-007-EXEMPLO/
├── README.md
├── TASK-1.md
└── TASK-2.md
```

`README.md`

```markdown
---
doc_id: "ISSUE-F1-01-007-EXEMPLO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "required"
---

## Tasks
- [TASK-1.md](./TASK-1.md)
- [TASK-2.md](./TASK-2.md)
```

Cada `TASK-N.md` deve seguir `TEMPLATE-TASK.md` e conter todos os campos minimos
listados nesta spec.

## Exemplo de Compatibilidade - Issue Legada Required

```markdown
---
doc_id: "ISSUE-F1-01-002-CRIAR-MIGRATION.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "required"
---

## Tarefas Decupadas
- [ ] T1: criar migration Alembic com campos novos e downgrade valido
- [ ] T2: atualizar modelo SQLModel e alinhar defaults
- [ ] T3: validar upgrade/downgrade em ambiente de teste

## Instructions por Task

### T1
- objetivo: criar migration com upgrade e downgrade seguros
- precondicoes: revision base identificada; nomes finais das colunas aprovados
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/versions/...`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. gerar ou criar o arquivo de migration sobre a revision correta
  2. adicionar as colunas novas no `upgrade()` com nullability e defaults definidos pela issue
  3. adicionar o `downgrade()` removendo apenas o que esta sendo criado nesta issue
- comandos_permitidos:
  - `cd backend && alembic upgrade head`
  - `cd backend && alembic downgrade -1`
- resultado_esperado: migration sobe e desce sem erro
- testes_ou_validacoes_obrigatorias:
  - `cd backend && alembic upgrade head`
  - `cd backend && alembic downgrade -1`
- stop_conditions:
  - parar se houver migration concorrente ou conflito de revision nao resolvido
```

## Exemplo Canonico - Frontend Simples

```markdown
---
doc_id: "ISSUE-F2-01-005-AJUSTAR-COPY-DO-BADGE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "optional"
---

## Tarefas Decupadas
- [ ] T1: ajustar o texto do badge no componente alvo
- [ ] T2: atualizar o teste unitario correspondente
```

## Commit apos Cada Task

- apos concluir cada task, o executor deve fazer commit antes de prosseguir
- formato da mensagem: ver `GOV-COMMIT-POR-TASK.md`
- a regra aplica-se a issues `optional` e `required`

## Checklist de Consistencia

Antes de marcar uma issue `required` como pronta para execucao, confirme:

- [ ] `task_instruction_mode: required` esta no frontmatter
- [ ] toda task possui detalhamento vinculante no formato escolhido (`TASK-N.md` ou bloco correspondente em `## Instructions por Task`)
- [ ] todo detalhamento por task tem os campos minimos
- [ ] os passos atomicos estao em ordem e sem branching pesado
- [ ] os testes obrigatorios estao declarados
- [ ] existe ao menos uma `stop_condition` objetiva por task
