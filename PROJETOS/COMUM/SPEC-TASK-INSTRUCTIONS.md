---
doc_id: "SPEC-TASK-INSTRUCTIONS.md"
version: "3.2"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SPEC-TASK-INSTRUCTIONS

## Objetivo

Definir como `instructions` atomicas devem viver dentro de `tasks` no modelo
canonico `feature -> user story -> task`, sem criar novo artefato raiz para
execucao.

## Conceitos

- `user story`: unidade documental completa de execucao
- `task`: menor unidade executavel dentro da user story
- `instruction`: menor unidade atomica de execucao dentro da task
- `depends_on`: relacao explicita de precedencia entre tasks da mesma user story
- `parallel_safe`: declaracao de elegibilidade para execucao paralela
- `write_scope`: lista parseavel de caminhos, modulos ou superficies tocadas

Checklist minima antes de `status: done` no `TASK-N.md`:

- `write_scope` cobre o que foi efetivamente entregue ou validado
- validacoes citadas em `testes_ou_validacoes_obrigatorias` (e `testes_red` se
  `tdd_aplicavel: true`) foram executadas com resultado coerente, ou a task foi
  `cancelled` com motivo
- se a task terminar `done`, o commit rastreavel da task existe conforme
  `GOV-COMMIT-POR-TASK.md`
- nao manter a task em `todo` quando a entrega ja esta no repo: regularizar
  `done` ou ajustar escopo em nova task

Regra canonica:

- `instruction` nunca vira arquivo independente
- `instruction` vive inline na user story legada, na secao `## Instructions por Task`, ou no corpo de
  `TASK-N.md` quando a user story for granularizada
- `task` pode ser checklist curto (user story legada) ou arquivo `TASK-N.md` (user story granularizada);
  `instruction` operacionaliza o como executar

## Campo Canonico da User Story

Toda user story nova ou revisada deve declarar no frontmatter:

```yaml
task_instruction_mode: "optional"
```

Valores aceitos:

- `optional`
- `required`

## Quando `required` e obrigatorio

Use `task_instruction_mode: required` quando a user story contiver qualquer um destes fatores:

- migration ou mudanca com persistencia/rollback sensivel
- ordem de execucao critica
- alteracao multi-camada ou multi-arquivo com dependencia forte
- remediacao originada de auditoria `hold`
- remediacao originada de revisao pos-user-story com risco alto ou regressao delicada
- handoff planejado para outra IA ou sessao

Se nenhum desses fatores existir, `optional` e o default recomendado.

## Estrutura Minima do Detalhamento por Task

Cabeçalhos opcionais de sessao (`imp-N.md`) alinhados a cada task:
`PROJETOS/COMUM/TEMPLATE-IMP-SESSAO.md`.

Quando `task_instruction_mode: required`, a user story precisa ter:

- tasks identificadas de forma rastreavel (`T1`, `T2`, `T3`...)
- um detalhamento vinculante por task no formato escolhido:
  - user story granularizada: um arquivo `TASK-N.md` por task
  - user story legada: secao `## Instructions por Task` com um bloco por task

Campos minimos por task:

- `user_story_id`
- `objetivo`
- `precondicoes`
- `depends_on`
- `parallel_safe`
- `write_scope`
- `arquivos_a_ler_ou_tocar`
- `tdd_aplicavel` (`true`, `false` ou omitido; omitido equivale a `false`)
- `testes_red` quando `tdd_aplicavel: true`
- `passos_atomicos`
- `comandos_permitidos`
- `resultado_esperado`
- `testes_ou_validacoes_obrigatorias`
- `stop_conditions`

Regras adicionais quando `tdd_aplicavel: true`:

- `testes_red` deve aparecer imediatamente antes de `passos_atomicos`
- `testes_red` deve listar os testes ou cenarios a escrever primeiro
- `testes_red` deve declarar o comando que executa esses testes
- `testes_red` deve declarar explicitamente que os testes precisam falhar antes da implementacao
- cada comando citado em `testes_red` tambem deve constar em `comandos_permitidos`
- `passos_atomicos` deve refletir a ordem TDD: escrever testes, rodar e confirmar falha, implementar minimo, rodar e confirmar sucesso, refatorar se necessario
- `testes_ou_validacoes_obrigatorias` permanece reservado para as validacoes finais, apos o green estar confirmado

Quando `tdd_aplicavel: false` ou o campo estiver omitido, `testes_red` nao e obrigatorio e a
task continua no comportamento atual.

Formato de `tdd_aplicavel`:

- user story granularizada: campo no frontmatter de `TASK-N.md`
- user story legada: campo inline no bloco `### Tn` dentro de `## Instructions por Task`

Formato dos novos metadados de orquestracao:

- `user_story_id`: ID canonico da user story dona da task
- `depends_on`: lista de `T<N>` dentro da mesma user story
- `parallel_safe`: `true` ou `false`
- `write_scope`: lista de caminhos ou superficies concretas; obrigatoria e
  especifica quando `parallel_safe: true`

## Criterio de Atomicidade

Uma instruction atomica deve:

- descrever uma unica acao verificavel por passo
- evitar branching pesado ou fluxos com muitas alternativas
- explicitar ordem quando a sequencia for critica
- quando `tdd_aplicavel: true`, separar claramente a fase red da fase green
- permitir que outro agente execute sem reinterpretar o objetivo da task
- dizer claramente quando parar e reportar bloqueio

Uma instruction ruim costuma:

- misturar varias alteracoes em um unico passo
- depender de conhecimento tacito nao documentado
- omitir arquivos ou testes obrigatorios
- em task TDD, tratar testes apenas como validacao final em vez de driver da implementacao
- usar formulacoes vagas como "ajustar se necessario" sem criterio objetivo

## Regra de Elegibilidade

- user story com `task_instruction_mode: required` sem detalhamento completo por task no formato escolhido nao e elegivel para execucao
- o agente executor deve responder `BLOQUEADO` em vez de improvisar
- o bloqueio vale tambem quando houver task sem `TASK-N.md` correspondente, sem bloco correspondente em `## Instructions por Task`, ou com campos minimos ausentes
- o bloqueio vale tambem quando `tdd_aplicavel: true` estiver sem `testes_red`, sem comando red,
  sem criterio explicito de falha inicial, ou sem `passos_atomicos` na ordem TDD
- o bloqueio vale tambem quando `depends_on` apontar para task inexistente ou
  ainda nao encerrada
- o bloqueio vale tambem quando `parallel_safe: true` estiver sem `write_scope`
  explicito e verificavel

## Compatibilidade de Rollout

- user stories antigas sem `task_instruction_mode` podem ser tratadas como `optional` ate serem revisadas
- nao ha retrofit em massa obrigatorio neste rollout
- qualquer user story nova de alto risco deve nascer com `task_instruction_mode: required`
- tasks sem `tdd_aplicavel` continuam compativeis e equivalem a `false`
- referencias legadas a `issue_id` podem ser lidas como compatibilidade
  documental, mas o contrato novo usa `user_story_id`
- antes de `ready_for_review`, a US deve passar em
  `scripts/framework_governance/validate_us_traceability.py`

## User Story Granularizada (Pasta com TASK-N.md)

Quando a user story for uma pasta `user-stories/US-*/` com `README.md` e `TASK-*.md`:

- cada task vive em arquivo proprio `TASK-N.md`; usar `TEMPLATE-TASK.md` como base
- o `README.md` contem o manifesto (User Story, Contexto, DoD, Dependencias) e lista de links
  para as tasks
- user stories legadas (arquivo unico `.md`) continuam validas; o executor detecta o formato
  e aplica o fluxo correto

## Exemplo Canonico - User Story Granularizada Required

```markdown
user-stories/US-1-01-EXEMPLO/
├── README.md
├── TASK-1.md
└── TASK-2.md
```

`README.md`

```markdown
---
doc_id: "US-1-01-EXEMPLO"
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

## Exemplo Canonico - TASK-N Backend com TDD

```markdown
---
doc_id: "TASK-1.md"
user_story_id: "US-1-01-EXEMPLO"
task_id: "T1"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/routers/ativacoes.py"
  - "backend/tests/test_ativacoes_router.py"
tdd_aplicavel: true
---

# T1 - Ajustar contrato do endpoint de ativacoes

## objetivo

Fazer o endpoint retornar o campo `slug` normalizado sem quebrar o contrato atual.

## precondicoes

- router atual identificado
- suite de testes HTTP da feature existente

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ativacoes.py`
- `backend/tests/test_ativacoes_router.py`

## testes_red

- testes_a_escrever_primeiro:
  - adicionar caso cobrindo resposta com `slug` normalizado
  - adicionar caso cobrindo ausencia de `slug` quando o nome vier vazio
- comando_para_rodar:
  - `cd backend && TESTING=true python -m pytest -q backend/tests/test_ativacoes_router.py -k slug`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar o comando red e confirmar falha real ligada ao contrato esperado
3. implementar o minimo necessario no endpoint para fazer apenas esses testes passarem
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes ou extracoes locais sem ampliar escopo, mantendo a suite green

## comandos_permitidos

- `cd backend && TESTING=true python -m pytest -q backend/tests/test_ativacoes_router.py -k slug`

## resultado_esperado

Endpoint retorna `slug` normalizado, com cobertura automatizada descrevendo o comportamento.

## testes_ou_validacoes_obrigatorias

- `cd backend && TESTING=true python -m pytest -q backend/tests/test_ativacoes_router.py`
- revisar resposta do endpoint contra os criterios de aceitacao da user story

## stop_conditions

- parar se os testes novos passarem antes de qualquer implementacao
- parar se o contrato atual observado divergir do manifesto da user story
```

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
- tdd_aplicavel: false
- passos_atomicos:
  1. gerar ou criar o arquivo de migration sobre a revision correta
  2. adicionar as colunas novas no `upgrade()` com nullability e defaults definidos pela issue legada
  3. adicionar o `downgrade()` removendo apenas o que esta sendo criado nesta issue legada
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
doc_id: "US-2-01-AJUSTAR-COPY-DO-BADGE.md"
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

## Exemplo Canonico - User Story Legada Required com TDD

```markdown
---
doc_id: "US-2-01-010-AJUSTAR-FILTRO-DE-BUSCA.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "required"
---

## Tarefas Decupadas
- [ ] T1: corrigir debounce do filtro no frontend

## Instructions por Task

### T1
- objetivo: corrigir debounce sem regressao visual ou funcional
- precondicoes: componente alvo identificado; suite do filtro existente
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/filtros/BuscaDebounced.tsx`
  - `frontend/src/features/filtros/BuscaDebounced.test.tsx`
- tdd_aplicavel: true
- testes_red:
  - testes_a_escrever_primeiro:
    - adicionar caso cobrindo disparo unico apos digitar rapidamente
    - adicionar caso cobrindo limpeza do timer no unmount
  - comando_para_rodar:
    - `cd frontend && npm run test -- BuscaDebounced.test.tsx --run`
  - criterio_red:
    - os testes devem falhar antes da implementacao; se ja passarem, parar e revisar o entendimento
- passos_atomicos:
  1. escrever os testes listados em `testes_red`
  2. rodar a suite alvo e confirmar falha inicial
  3. implementar o minimo necessario para fazer os testes passarem
  4. rodar novamente a suite alvo e confirmar green
  5. refatorar apenas nomes ou extracoes locais mantendo green
- comandos_permitidos:
  - `cd frontend && npm run test -- BuscaDebounced.test.tsx --run`
- resultado_esperado: filtro com debounce previsivel e cobertura automatizada
- testes_ou_validacoes_obrigatorias:
  - `cd frontend && npm run test -- BuscaDebounced.test.tsx --run`
  - validar manualmente que o filtro segue responsivo na tela alvo
- stop_conditions:
  - parar se os testes novos nao falharem antes da implementacao
  - parar se o componente real divergir do contrato descrito na user story
```

## Commit apos Cada Task

- apos concluir cada task, o executor deve fazer commit antes de prosseguir
- formato da mensagem: ver `GOV-COMMIT-POR-TASK.md`
- a regra aplica-se a user stories `optional` e `required`

## Checklist de Consistencia

Antes de marcar uma user story `required` como pronta para execucao, confirme:

- [ ] `task_instruction_mode: required` esta no frontmatter
- [ ] toda task possui detalhamento vinculante no formato escolhido (`TASK-N.md` ou bloco correspondente em `## Instructions por Task`)
- [ ] todo detalhamento por task tem os campos minimos
- [ ] os passos atomicos estao em ordem e sem branching pesado
- [ ] os testes obrigatorios estao declarados
- [ ] quando `tdd_aplicavel: true`, `testes_red` esta presente e separado das validacoes finais
- [ ] quando `tdd_aplicavel: true`, `passos_atomicos` explicita a ordem red -> green -> refactor
- [ ] existe ao menos uma `stop_condition` objetiva por task
