# Algoritmo do Framework de Projetos

Este documento consolida o algoritmo operacional de alto nivel do framework de
projetos do NPBB. Ele serve como mapa de execucao e governanca, mas nao
substitui os documentos normativos especializados em `PROJETOS/COMUM/`.

## Regra de Ouro

> "Se eu pegar qualquer item e perguntar: 'isso entrega algo utilizavel?',
> se a resposta for nao, a estrutura esta errada; se for sim, o recorte esta
> aderente ao framework."

## Frase Guia

> **"Intake descobre, PRD decide, Fase organiza, Epic agrupa, Issue delimita, Task executa, Auditoria valida"**

---

## 1. Premissas Canonicas

### 1.1 Delivery-First / Feature-First

O framework planeja por **features demonstraveis**, nao por camadas tecnicas.
Banco, backend, frontend, testes, observabilidade e rollout entram como impacto
da feature, nunca como eixo principal do plano.

### 1.2 Issue-First

A menor unidade documental completa de execucao e a **issue**:

- formato canonico: pasta `issues/ISSUE-.../` com `README.md` e `TASK-*.md`
- formato legado: arquivo unico `issues/ISSUE-....md`

A menor unidade executavel e a **task**. A menor unidade atomica e a
**instruction**, que vive dentro da task e nunca vira artefato raiz proprio.

### 1.3 Cadeia Canonica

```text
Intake -> PRD -> Fases -> Epicos -> Issues -> Tasks -> Auditorias
```

### 1.4 Rastreabilidade Obrigatoria

Toda implementacao deve preservar, sem ambiguidade:

```text
Feature do PRD -> Fase -> Epic -> Issue -> Task
```

Cada issue deve declarar explicitamente sua **Feature de Origem**.

### 1.5 Fontes de Verdade

Este arquivo nao redefine regras ja normatizadas. Para cada tema, a fonte
primaria e:

| Tema | Fonte primaria |
|---|---|
| mapa do framework | `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md` |
| cadeia de trabalho, status e DoD | `PROJETOS/COMUM/GOV-SCRUM.md` |
| intake e gate `Intake -> PRD` | `PROJETOS/COMUM/GOV-INTAKE.md` |
| estrutura de fase, epic, issue e sprint | `PROJETOS/COMUM/GOV-ISSUE-FIRST.md` |
| task instructions e elegibilidade | `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md` |
| work order e escopo executavel | `PROJETOS/COMUM/GOV-WORK-ORDER.md` |
| decisoes, risco e approvals | `PROJETOS/COMUM/GOV-DECISOES.md` |
| sprint limits | `PROJETOS/COMUM/GOV-SPRINT-LIMITES.md` |
| commit por task | `PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md` |
| auditoria e remediacao | `PROJETOS/COMUM/GOV-AUDITORIA.md` |
| branch strategy | `PROJETOS/COMUM/GOV-BRANCH-STRATEGY.md` |

### 1.6 Estrutura Canonica de Projeto

```text
PROJETOS/<PROJETO>/
  INTAKE-<PROJETO>.md
  PRD-<PROJETO>.md
  AUDIT-LOG.md
  DECISION-PROTOCOL.md                (opcional)
  feito/
  F<N>-<NOME-DA-FASE>/
    F<N>_<PROJETO>_EPICS.md
    EPIC-F<N>-<NN>-<NOME>.md
    issues/
      ISSUE-F<N>-<NN>-<MMM>-<NOME>/
        README.md
        TASK-1.md
        TASK-2.md
    sprints/
      SPRINT-F<N>-<NN>.md
    auditorias/
      RELATORIO-AUDITORIA-F<N>-R<NN>.md
```

---

## 2. Regras Estruturais Minimas

### 2.1 Status Canonicos

Status persistidos:

- `todo`
- `active`
- `done`
- `cancelled`

Estados operacionais, mas nao status documentais canonicos:

- `BLOQUEADO`
- `BLOCKED_LIMIT`

### 2.2 Gate de Auditoria da Fase

Estados operacionais do gate:

- `not_ready`
- `pending`
- `hold`
- `approved`

### 2.3 task_instruction_mode

Valores aceitos:

- `optional`
- `required`

Quando `required`, a issue so e elegivel se cada task tiver detalhamento
completo no formato canonico:

- `objetivo`
- `precondicoes`
- `arquivos_a_ler_ou_tocar`
- `tdd_aplicavel`
- `testes_red` quando `tdd_aplicavel: true`
- `passos_atomicos`
- `comandos_permitidos`
- `resultado_esperado`
- `testes_ou_validacoes_obrigatorias`
- `stop_conditions`

Se qualquer campo obrigatorio faltar, a execucao deve responder `BLOQUEADO`.

### 2.4 Decisao e Work Order

Toda execucao com side effect, persistencia ou custo relevante deve ser
entendida como governada por:

- uma **decision** proporcional ao risco (`R0` a `R3`)
- uma **work order** com escopo, risco, paths e output esperado

Regras minimas:

- `R2` e `R3` exigem `rollback_plan`
- aprovacao humana explicita e obrigatoria quando o side effect nao for
  trivialmente reversivel
- nenhuma execucao com contexto insuficiente pode ser tratada como `APPROVED`

---

## 3. Algoritmo Local do Framework

### 3.1 Planejamento

#### Passo 1: Criar ou revisar o Intake

Produzir `INTAKE-<PROJETO>.md` com problema, publico, fluxo principal, escopo,
metricas, restricoes, riscos e lacunas conhecidas.

#### Passo 2: Validar gate `Intake -> PRD`

O intake so pode subir de nivel quando atender a governanca de prontidao
definida em `GOV-INTAKE.md`.

#### Passo 3: Gerar o PRD

Produzir `PRD-<PROJETO>.md` com:

- features demonstraveis como eixo
- criterios de aceite por feature
- impactos arquiteturais por feature
- fases derivadas das features

#### Passo 4: Aprovar o PRD

Sem aprovacao do PRD, a derivacao para fases, epicos e issues nao avanca.

#### Passo 5: Planejar as Fases

Cada fase deve declarar:

- objetivo da fase
- gate de saida
- estado do gate de auditoria
- tabela de epicos
- dependencias
- escopo dentro/fora
- DoD da fase

#### Passo 6: Planejar os Epicos

Cada epic deve declarar:

- feature de origem
- comportamento coberto
- resultado de negocio mensuravel
- contexto arquitetural
- DoD do epic
- tabela de issues

#### Passo 7: Planejar as Issues

Cada issue deve declarar:

- user story
- feature de origem
- contexto tecnico
- plano TDD (`Red / Green / Refactor`)
- criterios `Given / When / Then`
- DoD da issue
- task_instruction_mode
- `decision_refs` quando houver decisao relevante

#### Passo 8: Detalhar as Tasks

Quando `task_instruction_mode: required`:

- usar issue granularizada
- detalhar `TASK-N.md` com todos os campos obrigatorios
- se houver codigo com cobertura automatizavel, a task deve declarar
  `tdd_aplicavel: true` e trazer `testes_red` antes de `passos_atomicos`

#### Passo 9: Planejar a Sprint

`SPRINT-*.md` existe apenas para selecao operacional e capacidade. Ele nao
substitui issue, epic ou fase como fonte de verdade.

Antes de incluir itens na sprint, validar:

- maximo `5` issues por sprint
- maximo `13` story points
- issue com ate `5` story points
- task com ate `1 dia util ou 3 story points`
- maximo `8` tasks por issue

Se um limite for violado, o estado operacional e `BLOCKED_LIMIT`.

### 3.2 Preflight de Execucao

#### Passo 10: Selecionar a proxima issue elegivel

Uma issue e elegivel quando:

- esta em `todo` ou `active`
- existe task `todo`
- a rastreabilidade para feature, epic e fase esta integra
- o formato da issue esta aderente a `GOV-ISSUE-FIRST.md`

#### Passo 11: Validar elegibilidade da task

Antes de executar:

- se `task_instruction_mode: required`, confirmar existencia de `TASK-N.md`
- validar todos os campos obrigatorios
- se `tdd_aplicavel: true`, validar existencia de `testes_red`, comando red e
  criterio explicito de falha inicial

Falha nessa verificacao implica `BLOQUEADO`.

#### Passo 12: Verificar contexto de risco e decisao

Antes de qualquer acao material:

- classificar risco da execucao
- verificar `decision_refs` da issue
- garantir rollback claro em `R2` ou `R3`
- exigir approval humano quando o efeito nao for trivialmente reversivel

#### Passo 13: Verificar defasagem documental e auditoria

Se a issue estiver ligada a auditoria anterior ou review pos-issue:

1. ler `AUDIT-LOG.md`
2. identificar se ha rodada posterior que superou o contexto
3. decidir se a issue segue valida, desatualizada ou cancelada

### 3.3 Execucao da Issue

#### Passo 14: Executar uma task por vez

A ordem operacional e sempre:

1. selecionar a task elegivel
2. executar o que esta documentado
3. validar o resultado
4. fazer commit
5. atualizar o estado documental

Nao e permitido pular direto para fechamento da issue sem concluir o ciclo por
task.

#### Passo 15: Aplicar TDD quando requerido

Quando `tdd_aplicavel: true`, a ordem minima e:

1. escrever os testes descritos em `testes_red`
2. rodar o comando red e confirmar falha real
3. implementar o minimo necessario para green
4. rodar as validacoes finais
5. refatorar sem ampliar escopo

Se os testes passarem antes da implementacao, a task deve parar e reportar
bloqueio ou divergencia de contexto.

#### Passo 16: Commit apos cada task

Ao concluir cada task, fazer commit obrigatorio no formato:

```text
<PROJETO> <ISSUE_ID> <TASK_ID>: <descricao breve>
```

Sem commit por task, a cascata de fechamento nao deve ser executada.

### 3.4 Cascata de Fechamento

#### Passo 17: Fechar a issue

Ao concluir todas as tasks:

- marcar a issue como `done`
- atualizar `last_updated`
- fechar o DoD da issue

#### Passo 18: Atualizar o epic pai

- atualizar a linha da issue na tabela do epic
- se todas as issues do epic estiverem encerradas (`done` ou `cancelled`),
  marcar o epic como `done`
- caso contrario, manter `active`

#### Passo 19: Atualizar o manifesto da fase

- atualizar a linha do epic
- se todos os epicos estiverem `done`, mover `audit_gate` para `pending`
- a fase nunca vai direto para `done` sem auditoria `go`

#### Passo 20: Atualizar a sprint

- atualizar a linha da issue em `SPRINT-*.md`
- se todas as issues selecionadas estiverem encerradas, marcar a sprint como
  `done`

Regra da cascata:

```text
issue -> epic -> fase -> sprint
```

### 3.5 Review Pos-Issue

#### Passo 21: Revisar a issue quando solicitado

A review pos-issue e opcional. Ela:

- nao substitui a auditoria formal da fase
- nao reabre automaticamente a issue original
- julga diffs, cobertura, risco e aderencia ao manifesto

Vereditos canonicos:

- `aprovada`
- `correcao_requerida`
- `cancelled`

#### Passo 22: Materializar follow-up de review

Se houver `correcao_requerida`:

- ajuste local e contido -> abrir `issue-local` na mesma fase/epic
- remediacao estrutural ou sistemica -> abrir `INTAKE-<PROJETO>-<SLUG>.md`

Se a fase ja estiver com `audit_gate: approved`, nao abrir issue local na fase
fechada; a remediacao deve seguir fluxo proprio.

### 3.6 Auditoria de Fase

#### Passo 23: Verificar elegibilidade para auditoria

A fase so pode entrar em auditoria quando:

- todos os epicos estiverem `done`
- o gate da fase estiver em `pending`
- os insumos obrigatorios estiverem disponiveis
- houver commit base auditavel
- a worktree estiver limpa para permitir veredito final

Se a worktree estiver suja, a rodada pode existir apenas como `provisional` e
nao pode aprovar gate.

#### Passo 24: Executar a auditoria

Cada rodada deve produzir:

- `auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md`
- nova entrada em `AUDIT-LOG.md`
- atualizacao do gate da fase

Vereditos permitidos:

- `go`
- `hold`
- `cancelled`

Achados devem ter evidencia. Opiniao sem evidencias nao e achado valido.

#### Passo 25: Tratar hold

Se a auditoria resultar em `hold`, cada follow-up bloqueante deve virar um dos
destinos canonicos:

- `issue-local`
- `new-intake`
- `cancelled`

O gate da fase permanece `hold` ate nova rodada com veredito `go`.

#### Passo 26: Fechar a fase

Quando a auditoria emitir `go`:

- atualizar o gate para `approved`
- consolidar evidencias no `AUDIT-LOG.md`
- mover a pasta da fase para `<PROJETO>/feito/`

So apos isso a fase pode ser tratada como encerrada.

---

## 4. Regras de Bloqueio

O algoritmo deve parar e responder `BLOQUEADO` quando ocorrer qualquer uma das
condicoes abaixo:

- issue `required` sem `TASK-N.md` ou sem campos obrigatorios
- task TDD sem `testes_red`, comando red ou criterio de falha inicial
- rastreabilidade quebrada entre feature, epic, issue e task
- item acima dos limites de sprint sem decomposicao ou override valido
- side effect relevante sem decisao ou sem approval exigido
- issue derivada de auditoria ou review com contexto superado por rodada mais
  recente
- tentativa de promover fase para `done` sem auditoria `go`
- tentativa de auditar fase com worktree suja como se fosse rodada final

---

## 5. Estrategia de Branches

Regra principal:

> **Branch por feature, nao por camada**

Formato canonico:

```text
feature/<id-feature-normalizado>-<slug>
```

Exemplos validos:

- `feature/feature-1-cadastro-usuario`
- `feature/feature-2-login`

Exemplos invalidos:

- `feature/backend-login`
- `feature/frontend-login`
- `feature/database-login`

Excecoes legitimas:

- `infra/<slug>` para fundacao transversal genuina
- `bugfix/<ID-ISSUE>-<slug>`
- `hotfix/<slug>`
- `refactor/<slug>`
- `audit/<FASE>-R<NN>`

---

## 6. Resumo Executivo do Fluxo

```text
INTAKE
  -> PRD
  -> FASE
  -> EPIC
  -> ISSUE
  -> TASK
  -> COMMIT POR TASK
  -> FECHAMENTO issue -> epic -> fase -> sprint
  -> AUDITORIA DE FASE
       -> GO   -> gate approved -> mover para feito/
       -> HOLD -> follow-up -> nova execucao -> nova auditoria
```

## 7. Regra Final

O framework local nao opera por improviso. Sempre que houver conflito entre este
mapa e um documento normativo especializado de `PROJETOS/COMUM/`, prevalece o
documento especializado.
